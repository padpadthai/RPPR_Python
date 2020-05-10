import calendar
import datetime
import logging
from typing import List, Dict

import chart_studio
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pandas import DataFrame
from scipy.stats import ttest_ind, levene, shapiro, mannwhitneyu

from app import config, secrets
from app.transformer import TransformedPropertySale

pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 200)
pd.set_option('display.max_rows', 1000)

pio.templates.default = config['plotly']['template']
chart_studio.tools.set_credentials_file(username=config['plotly']['chart-studio']['username'],
                                        api_key=secrets['api-key']['chart-studio'])


class Analyser:

    def __init__(self, property_sales: List[TransformedPropertySale]):
        self.property_sales = property_sales
        self.data_frame = self.__pandas_setup()
        self.plots: List[Dict] = []

    def log_totals(self):
        logging.info("sales: '{}'".format(len(self.property_sales)))
        logging.info("new property sales: '{}'".format(
            self.__count_with_lambda(lambda sale: sale.new, self.property_sales)))
        logging.info("non-new property sales: '{}'".format(
            self.__count_with_lambda(lambda sale: not sale.new, self.property_sales)))
        logging.info("full price property sales: '{}'".format(
            self.__count_with_lambda(lambda sale: sale.full_price, self.property_sales)))
        logging.info("non-full price property sales: '{}'".format(
            self.__count_with_lambda(lambda sale: not sale.full_price, self.property_sales)))
        logging.info("vat exclusive property sales: '{}'".format(
            self.__count_with_lambda(lambda sale: sale.vat_exclusive, self.property_sales)))
        logging.info("vat inclusive property sales: '{}'".format(
            self.__count_with_lambda(lambda sale: not sale.vat_exclusive, self.property_sales)))

    @classmethod
    def __count_with_lambda(cls, lambda_func, sales: List[TransformedPropertySale]) -> int:
        return len(list(filter(lambda_func, sales)))

    def __pandas_setup(self) -> DataFrame:
        dict_property_sales = [{
            'date': sale.date, 'county': sale.county, 'price': sale.price, 'full_price': sale.full_price,
            'vat_exclusive': sale.vat_exclusive, 'new': sale.new, 'size': sale.size
        } for sale in self.property_sales]
        data_frame = pd.DataFrame(data=dict_property_sales)
        data_frame['price'] = pd.to_numeric(data_frame['price'])
        data_frame['date'] = pd.to_datetime(data_frame['date'])
        return data_frame

    def get_descriptives(self) -> List[Dict]:
        dicts = [{'name': 'overall', 'data': self.__format_descriptives(self.data_frame)},
                 {'name': 'full_price', 'data': self.__format_descriptives(self.data_frame[self.data_frame['full_price']])},
                 {'name': 'county', 'data': self.__format_descriptives(self.data_frame.groupby('county'))},
                 {'name': 'new', 'data': self.__format_descriptives(self.data_frame[self.data_frame['new']])},
                 {'name': 'full_price_per_county',
                  'data': self.__format_descriptives(self.data_frame[self.data_frame['full_price'] == True].groupby('county'))},
                 {'name': 'new_per_county',
                  'data': self.__format_descriptives(self.data_frame[self.data_frame['new'] == True].groupby('county'))},
                 {'name': 'full_price_new',
                  'data': self.__format_descriptives(self.data_frame[(self.data_frame['new'] == True) & (self.data_frame['full_price'] == True)])},
                 {'name': 'year',
                  'data': self.__format_descriptives(self.data_frame.groupby(self.data_frame['date'].map(lambda x: x.year)))},
                 {'name': 'full_price_per_year',
                  'data': self.__format_descriptives(self.data_frame[self.data_frame['full_price'] == True].groupby(self.data_frame['date'].map(lambda x: x.year)))},
                 {'name': 'new_per_year',
                  'data': self.__format_descriptives(self.data_frame[self.data_frame['new'] == True].groupby(self.data_frame['date'].map(lambda x: x.year)))},
                 {'name': 'full_price_new_per_year',
                  'data': self.__format_descriptives(self.data_frame[(self.data_frame['new'] == True) & (self.data_frame['full_price'] == True)].groupby(self.data_frame['date'].map(lambda x: x.year)))},
                 {'name': 'county_per_year',
                  'data': self.__format_descriptives(self.data_frame.groupby([self.data_frame['date'].map(lambda x: x.year)]))},
                 {'name': 'full_price_per_county_per_year',
                  'data': self.__format_descriptives(self.data_frame[self.data_frame['full_price'] == True].groupby([self.data_frame['date'].map(lambda x: x.year), 'county']))},
                 {'name': 'full_price_new_per_county_per_year', 'data': self.__format_descriptives(self.data_frame[(self.data_frame['new'] == True) & (self.data_frame['full_price'] == True)].groupby([self.data_frame['date'].map(lambda x: x.year), 'county']))}]
        return dicts

    @classmethod
    def __format_descriptives(cls, data_frame: DataFrame) -> DataFrame:
        return data_frame.agg({'price': ['count', 'sum', 'mean', 'median', 'std', 'var', 'sem', 'min', 'max']})

    def time_analysis(self,):
        logging.debug("Plotting overall time series trend")
        month_yearly_grouped = self.__group_price_by_month(self.data_frame)
        month_yearly_figure = go.Figure(
            data=go.Scatter(x=month_yearly_grouped['date'], y=month_yearly_grouped['price_median'],
                            mode='lines', line={'width': 4}))
        month_yearly_figure.update_layout(title='Overall Property Sales Prices (Median per Month)', xaxis_title='Date',
                                          yaxis_title='Price (€)')
        self.plots.append({'name': 'irish_property_sales_prices_median_per_month_year', 'figure': month_yearly_figure})
        monthly_grouped = self.__group_price_by_month(self.data_frame, map_func=lambda raw_date: raw_date.month)
        monthly_grouped['label'] = monthly_grouped['date'].transform(lambda month_int: calendar.month_name[month_int])
        monthly_grouped['colour'] = 'paleturquoise'
        monthly_grouped.loc[3:6, 'colour'] = 'orange'
        monthly_grouped.loc[6:9, 'colour'] = 'indianred'
        monthly_grouped.loc[9:12, 'colour'] = 'midnightblue'
        monthly_figure = go.Figure()
        monthly_figure.add_trace(go.Bar(x=monthly_grouped['price_median'], y=monthly_grouped['label'], orientation='h',
                                        text=monthly_grouped['price_median'], textposition='auto',
                                        marker={'color': monthly_grouped['colour']}))
        monthly_figure.update_layout(title='Monthly Property Sales Prices (Median Sum)',
                                     xaxis={'title': 'Price (€)'}, yaxis={'title': 'Month', 'autorange': 'reversed'})
        self.plots.append({'name': 'irish_property_sales_prices_median_per_month', 'figure': monthly_figure})

    @classmethod
    def __group_price_by_month(cls, data_frame: DataFrame, sort_grouping=True, aggregation='median',
                                      map_func=lambda raw_date: datetime.datetime(month=raw_date.month,
                                                                                  year=raw_date.year,
                                                                                  day=1)) -> DataFrame:
        grouped = data_frame.groupby([data_frame['date'].map(map_func)], sort=sort_grouping) \
            .agg({'price': [aggregation]}).reset_index()
        grouped.columns = ['_'.join(col).rstrip('_') for col in grouped.columns.values]
        return grouped

    def new_old_analysis(self):
        logging.info("Analysing newly-built vs existing property sales using monthly medians")
        new = self.__group_price_by_month(self.data_frame[(self.data_frame['new'] == True)])
        old = self.__group_price_by_month(self.data_frame[(self.data_frame['new'] == False)])
        distribution = self.__group_price_by_month(self.data_frame)
        # hist_fig = px.histogram(distribution, x='price_median')
        # hist_fig.show()
        shapiro_tests = [shapiro(distribution['price_median'][(self.data_frame['new'] == cond)]) for cond in [True, False]]
        levene_test = levene(new['price_median'], old['price_median'])
        if shapiro_tests[0][1] > .05 and shapiro_tests[1][1] > .05 and levene_test[1] > .05:
            logging.debug("Median monthly prices appear to meet the assumptions for independent t-test")
            statistic = ttest_ind(new['price_median'], old['price_median'])
        else:
            logging.debug("Median monthly prices don't appear to meet the assumptions parametric statistics")
            statistic = mannwhitneyu(new['price_median'], old['price_median'])
        if statistic[1] < .05:
            logging.info(
                "There is a significant statistical difference between the sales prices of new and existing properties - statistic: '{}', p-value: '{}'".format(
                    statistic[0], statistic[1]))
        else:
            logging.info(
                "There is no statistically significant difference between the sales prices of new and existing properties - statistic: '{}', p-value: '{}'".format(
                    statistic[0], statistic[1]))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=new['date'], y=new['price_median'], mode='lines', name='New Build', line={'width': 4}))
        fig.add_trace(go.Scatter(x=old['date'], y=old['price_median'], mode='lines', name='Existing', line={'width': 4}))
        fig.update_layout(title='New & Existing Property Sales Prices (Median per Month)',
                          xaxis_title='Date', yaxis_title='Price (€)')
        self.plots.append({'name': 'new_v_existing_irish_property_sales_prices_median_per_month_year', 'figure': fig})
        count_new = self.__group_price_by_month(self.data_frame[(self.data_frame['new'] == True)], aggregation='count')
        count_fig = go.Figure()
        count_fig.add_trace(go.Scatter(x=new['date'], y=count_new['price_count'], mode='lines', line={'width': 4}))
        count_fig.update_layout(title='New Properties Sold (per Month)', xaxis_title='Date',
                                yaxis_title='Number of new properties sold')
        self.plots.append({'name': 'new_irish_property_sales_count_per_month_year', 'figure': count_fig})

    def output_plots(self):
        for plot in self.plots:
            plot['figure'].write_html(config['analysis']['plots']['output']['path'] + plot['name'] + ".html")

    def show_plots(self):
        for plot in self.plots:
            plot['figure'].show()

    def upload_plots_to_chart_studio(self):
        for plot in self.plots:
            chart_studio.plotly.plot(plot['figure'], filename=plot['name'])


def __seasonal_month(month: int) -> str:
    if month in range(0, 3):
        return 'Q1'
    elif month in range(3, 6):
        return 'Q2'
    elif month in range(6, 9):
        return 'Q3'
    else:
        return 'Q4'
