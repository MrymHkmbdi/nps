import streamlit as st
import numpy as np
import pandas as pd
import jdatetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib.colors import LinearSegmentedColormap
from persiantools.jdatetime import JalaliDate
from read_gsheet import fetch_gsheet_data
from fetch_metabase_data import fetch_metabase_data

import warnings

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title='Streamlit Dashboard',
    page_icon=':bar_chart:',
    layout='wide',
    initial_sidebar_state='expanded'
)

final_reasons_dict_list = {
    'thirdparty_main_suggesting_reason': ['سهولت خرید بیمه\u200cنامه', 'قیمت پایین\u200cتر بیمه\u200cنامه',
                                          'سرعت بالای صدور بیمه\u200cنامه', 'امکان مقایسه همه شرکت\u200cهای بیمه',
                                          'امکان خرید در همه ساعات شبانه روز', 'ارسال بیمه\u200cنامه به سراسر ایران',
                                          'پشتیبانی مناسب'],
    'carbody_main_suggesting_reason': ['سهولت خرید بیمه\u200cنامه', 'امکان مقایسه بین شرکت\u200cهای بیمه',
                                       'قیمت پایین\u200cتر بیمه\u200cنامه', 'بازدید راحت خودرو',
                                       'سرعت بالای صدور بیمه\u200cنامه',
                                       'ارسال بیمه\u200cنامه به سراسر ایران', 'امکان خرید در همه ساعات شبانه روز',
                                       'پشتیبانی مناسب'],
    'main_inspection_problem': ['نتوانستم در زمان اعلامی در محل بازدید حضور پیدا کنم.', 'فرایند بازدید طولانی بود.',
                                'نتوانستم زمان بازدید مورد نظرم را در سایت انتخاب کنم.',
                                'کارشناس بازدید در وقت مقرر حاضر نشد.',
                                'از من درخواست شد که خودرو مجددا بازدید شود.', 'کارشناس بازدید برخورد نامناسب داشت.'],
    'main_issuance_problem': ['مشکلات مربوط به قیمت',
                              'نقص مدارک اعلام شد و علارغم بارگذاری مدارک، بیمه نامه با تاخیر صادر شد.',
                              'علارغم کامل بودن مدارک، بیمه\u200cنامه با تاخیر صادر شد.',
                              'اطلاعات مندرج در بیمه\u200cنامه اشتباه ثبت شد.',
                              'نقص مدارک به من دیر اعلام شد.'],
    'main_callcenter_problem': ['کارشناس رفتار بدی با من داشت.', 'مدت انتظار برای پاسخ\u200cدهی طولانی بود.',
                                'کارشناس مشکل من را حل نکرد.', 'کیفیت تماس بد بود. (قطعی یا کیفیت بد صدا)',
                                'کارشناس اطلاعات و دانش کافی برای پاسخ به من را نداشت.'],
    'main_website_ordering_problem': ['در ورود به سایت مشکل داشتم. (وارد کردن کد تایید)',
                                      'نیاز به وارد کردن اطلاعات زیاد در سایت وجود دارد.',
                                      'عدم اعمال کد تخفیف', 'سایت کند بود و درست لود نمی\u200cشد.',
                                      'در مرحله پرداخت مشکل داشتم.',
                                      'در بارگذاری مدارک مشکل داشتم.'],
    'main_bb_trust_problem': ['در خرید\u200cهای قبلی تجربه بدی داشتم.',
                              'کلا به پلتفرم\u200cهای فروش آنلاین بیمه اعتماد کمی دارم.',
                              'نسبت به اعتبار بیمه\u200cنامه صادر شده عدم اطمینان دارم.'],
    'main_price_problem': ['درخواست واریز مبلغ اضافی', 'تخفیف کم در بیمه\u200cبازار',
                           'همین بیمه\u200cنامه را می\u200cتوانستم با قیمت کمتری بخرم.',
                           'محاسبه اشتباه قیمت بیمه\u200cنامه']
}

thirdparty_final_reasons_dict_list = {
    'main_suggesting_reason': ['سهولت خرید بیمه\u200cنامه',
                               'قیمت پایین\u200cتر بیمه\u200cنامه',
                               'سرعت بالای صدور بیمه\u200cنامه',
                               'امکان مقایسه بین شرکت\u200cهای بیمه',
                               'امکان خرید در همه ساعات شبانه روز',
                               'پشتیبانی مناسب'],
    'main_issuance_problem': ['اطلاعات مندرج در بیمه\u200cنامه اشتباه ثبت شد.',
                              'نقص مدارک به من دیر اعلام شد.',
                              'تاخیر در صدور بیمه‌نامه'],
    'main_callcenter_problem': ['مورد اعلام شده به پشتیبانی پیگیری نشد.',
                                'مدت انتظار برای پاسخ‌دهی پشتیبانی طولانی بود.',
                                'پاسخ مناسب از واحد پشتیبانی دریافت نکردید.'],
    'main_website_ordering_problem': ['کد تخفیف اعمال نشد.',
                                      'سایت کند بود و صفحات با تاخیر باز می‌شد.',
                                      'درگاه پرداخت مشکل داشت.',
                                      'نیاز به وارد کردن اطلاعات زیاد در سایت وجود دارد.',
                                      'راهنمایی کافی برای ثبت سفارش وجود نداشت.',
                                      'در بارگذاری مدارک مشکل داشتم.',
                                      'کد تایید ورود به سایت مشکل داشت.'],
    'main_payment_problem': ['تخفیف کمتر از مبلغ اعلامی بود.',
                             'از شما مبلغ بیشتر درخواست شد.',
                             'با شرایط مشابه قیمت پایین‌تر سراغ داشتید.',
                             'فاکتور شفافیت نداشت.']
}

carbody_final_reasons_dict_list = {
    'main_suggesting_reason': ['سهولت خرید بیمه\u200cنامه',
                               'امکان مقایسه بین شرکت\u200cهای بیمه',
                               'قیمت پایین\u200cتر بیمه\u200cنامه',
                               'بازدید راحت خودرو',
                               'سرعت بالای صدور بیمه\u200cنامه',
                               'ارسال بیمه\u200cنامه به سراسر ایران',
                               'امکان خرید در همه ساعات شبانه روز',
                               'پشتیبانی مناسب'],
    'main_inspection_problem': ['نتوانستم در زمان اعلامی در محل بازدید حضور پیدا کنم.', 'فرایند بازدید طولانی بود.',
                                'نتوانستم زمان بازدید مورد نظرم را در سایت انتخاب کنم.',
                                'کارشناس بازدید در وقت مقرر حاضر نشد.',
                                'از من درخواست شد که خودرو مجددا بازدید شود.', 'کارشناس بازدید برخورد نامناسب داشت.'],
    'main_issuance_problem': ['اطلاعات مندرج در بیمه\u200cنامه اشتباه ثبت شد.',
                              'نقص مدارک به من دیر اعلام شد.',
                              'تاخیر در صدور بیمه‌نامه'],
    'main_callcenter_problem': ['مورد اعلام شده به پشتیبانی پیگیری نشد.',
                                'مدت انتظار برای پاسخ‌دهی پشتیبانی طولانی بود.',
                                'پاسخ مناسب از واحد پشتیبانی دریافت نکردید.'],
    'main_website_ordering_problem': ['کد تخفیف اعمال نشد.',
                                      'سایت کند بود و صفحات با تاخیر باز می‌شد.',
                                      'درگاه پرداخت مشکل داشت.',
                                      'نیاز به وارد کردن اطلاعات زیاد در سایت وجود دارد.',
                                      'راهنمایی کافی برای ثبت سفارش وجود نداشت.',
                                      'در بارگذاری مدارک مشکل داشتم.',
                                      'کد تایید ورود به سایت مشکل داشت.'],
    'main_payment_problem': ['تخفیف کمتر از مبلغ اعلامی بود.',
                             'از شما مبلغ بیشتر درخواست شد.',
                             'با شرایط مشابه قیمت پایین‌تر سراغ داشتید.',
                             'فاکتور شفافیت نداشت.']
}

reasons_display_dict = {
    'Promoting Reasons': 'main_suggesting_reason',
    'Inspection Problems': 'main_inspection_problem',
    'Issuance Problems': 'main_issuance_problem',
    'CallCenter Problems': 'main_callcenter_problem',
    'Website Problems': 'main_website_ordering_problem',
    'Payment Problems': 'main_payment_problem',
}

# overall_integrated_data = pd.read_csv('integrated_data.csv')

def create_pivot_table(uploaded_data, start_date_input, end_date_input, the_type):
    nps_data = uploaded_data
    if the_type == 'thirdparty':
        english_columns = ['nps_score', 'main_ordering_reason', 'main_suggesting_reason',
                           'main_not_suggesting_reason',
                           'main_issuance_problem',
                           'main_callcenter_problem',
                           'main_website_ordering_problem',
                           'main_payment_problem']
        nps_data.rename(columns=dict(zip(list(nps_data.columns[2:10]),
                                         english_columns)), inplace=True)
        nps_data.rename(columns={'اسپم': 'spam', 'تاریخ شروع': 'start_date',
                                 'type': 'type'}, inplace=True)
        columns_to_drop = [0, 1, 10, 11, 12, 13, 15, 17, 18, 20, 22, 23, 24, 25, 26, 27, 29]

        nps_data = nps_data.drop(nps_data.columns[[col for col in columns_to_drop]], axis=1)
        nps_data = nps_data[nps_data['spam'].isnull()]
        nps_data.reset_index(inplace=True)
        nps_data = nps_data[['nps_score', 'main_ordering_reason', 'main_suggesting_reason',
                             'main_not_suggesting_reason',
                             'main_issuance_problem',
                             'main_callcenter_problem',
                             'main_website_ordering_problem',
                             'main_payment_problem', 'tracking_code', 'province',
                             'spam', 'start_date']]

    if the_type == 'carbody':
        english_columns = ['nps_score', 'main_ordering_reason', 'main_suggesting_reason',
                           'main_not_suggesting_reason',
                           'main_inspection_problem',
                           'main_issuance_problem',
                           'main_callcenter_problem',
                           'main_website_ordering_problem',
                           'main_payment_problem']
        nps_data.rename(columns=dict(zip(list(nps_data.columns[2:11]),
                                         english_columns)), inplace=True)
        nps_data.rename(columns={'اسپم': 'spam', 'تاریخ شروع': 'start_date',
                                 'type': 'type'}, inplace=True)
        columns_to_drop = [0, 11, 12, 13, 14, 15, 16, 18, 21, 23, 24, 25, 26, 27, 28, 30]

        nps_data = nps_data.drop(nps_data.columns[[col for col in columns_to_drop]], axis=1)
        nps_data = nps_data[nps_data['spam'].isnull()]
        nps_data.reset_index(inplace=True)
        nps_data = nps_data[['nps_score', 'main_ordering_reason', 'main_suggesting_reason',
                             'main_not_suggesting_reason',
                             'main_inspection_problem',
                             'main_issuance_problem',
                             'main_callcenter_problem',
                             'main_website_ordering_problem',
                             'main_payment_problem', 'tracking_code', 'province',
                             'spam', 'start_date']]

    def extract_reasons(reasons_list, column_name):
        for i in range(len(nps_data)):
            if pd.notna(nps_data.loc[i, column_name]):
                for c in nps_data.loc[i, column_name].split(','):
                    reasons_list.append(c.strip())

    nps_data.reset_index(inplace=True)

    nps_data['gregorian_start_date'] = nps_data['start_date'].apply(convert_jalali_to_gregorian)

    start_date_gregorian = jdatetime.date(*map(int, start_date_input.split('/'))).togregorian()
    end_date_gregorian = jdatetime.date(*map(int, end_date_input.split('/'))).togregorian()

    mask = (nps_data['gregorian_start_date'] >= pd.Timestamp(start_date_gregorian)) & (
            nps_data['gregorian_start_date'] <= pd.Timestamp(end_date_gregorian))
    filtered_data = nps_data[mask]

    if the_type == 'thirdparty':
        main_reasons_list = []
        for col in ['main_suggesting_reason',
                    'main_not_suggesting_reason',
                    'main_issuance_problem',
                    'main_callcenter_problem',
                    'main_website_ordering_problem',
                    'main_payment_problem']:
            extract_reasons(main_reasons_list, col)

    if the_type == 'carbody':
        main_reasons_list = []
        for col in ['main_suggesting_reason',
                    'main_not_suggesting_reason',
                    'main_inspection_problem',
                    'main_issuance_problem',
                    'main_callcenter_problem',
                    'main_website_ordering_problem',
                    'main_payment_problem']:
            extract_reasons(main_reasons_list, col)
    zero_data = {r: [0] * len(filtered_data) for r in main_reasons_list}
    zero_data['tracking_code'] = filtered_data['tracking_code'].copy()
    zero_data['score'] = filtered_data['nps_score'].copy()
    zero_data['start_date'] = filtered_data['start_date'].copy()
    final_result = pd.DataFrame(zero_data)
    final_result.set_index('tracking_code', inplace=True)

    if the_type == 'thirdparty':
        columns_to_check = [
            'main_ordering_reason', 'main_suggesting_reason',
            'main_not_suggesting_reason',
            'main_issuance_problem',
            'main_callcenter_problem',
            'main_website_ordering_problem',
            'main_payment_problem'
        ]
    else:
        columns_to_check = [
            'main_ordering_reason', 'main_suggesting_reason',
            'main_not_suggesting_reason',
            'main_inspection_problem',
            'main_issuance_problem',
            'main_callcenter_problem',
            'main_website_ordering_problem',
            'main_payment_problem'
        ]

    def convert_to_list(reasons_str):
        if pd.notna(reasons_str):
            r_list = reasons_str.split(',')
            final_list = [r.strip() for r in r_list]
            return final_list
        else:
            return []

    for cc in columns_to_check:
        filtered_data[cc] = filtered_data[cc].apply(convert_to_list)

    for _, row in filtered_data.iterrows():
        tracking_code = row['tracking_code']
        for col in columns_to_check:
            for value in row[col]:
                if value in final_result.columns:
                    final_result.at[tracking_code, value] = 1

    final_result.reset_index(inplace=True)
    final_result.dropna(subset=['score'], inplace=True)
    final_result.reset_index(drop=True, inplace=True)

    return final_result


@st.cache_data
def load_data(path: str):
    data_ = pd.read_csv(path)
    return data_


def convert_jalali_to_gregorian(jalali_str):
    if " - " in jalali_str:
        date_part, _ = jalali_str.split(" - ")
        # year, month, day = map(int, date_part.split("/"))
        # gregorian_date = jdatetime.date(year, month, day).togregorian()
        # return pd.Timestamp(gregorian_date)
    else:
        date_part = jalali_str
    year, month, day = map(int, date_part.split("/"))
    gregorian_date = jdatetime.date(year, month, day).togregorian()
    return pd.Timestamp(gregorian_date).tz_localize(None)


def convert_gregorian_to_jalali(gregorian_date):
    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
    return jalali_date.strftime('%Y/%m/%d')


def get_jalali_period(res_df):
    res_df['gregorian_start_date'] = pd.to_datetime(res_df['gregorian_start_date'])
    periods = []

    for date in res_df['gregorian_start_date']:
        jalali_date = JalaliDate.to_jalali(date)
        if aggregation_level == "Weekly":
            start_of_week = jalali_date - pd.Timedelta(days=jalali_date.weekday() + 1)
            periods.append(start_of_week)
        elif aggregation_level == "Monthly":
            start_of_month = JalaliDate(jalali_date.year, jalali_date.month, 1)
            periods.append(start_of_month)
        elif aggregation_level == "Seasonally":
            start_month = 1 + 3 * ((jalali_date.month - 1) // 3)
            start_of_quarter = JalaliDate(jalali_date.year, start_month, 1)
            periods.append(start_of_quarter)

    res_df['jalali_period'] = periods
    return res_df


def get_key_by_value(d, target_value):
    for key, value in d.items():
        if value == target_value:
            return key
    return None


def calculate_nps_score(res_df):
    conditions = [
        res_df['score'].isin([9, 10]),
        res_df['score'].between(7, 8),
        res_df['score'] < 7
    ]

    nps_groups = ['promoter', 'passive', 'detractor']

    res_df['nps_group'] = np.select(conditions, nps_groups, default='unknown')
    promoters_percent = (len(res_df[res_df['nps_group'] == 'promoter']) / len(res_df)) * 100
    detractors_percent = (len(res_df[res_df['nps_group'] == 'detractor']) / len(res_df)) * 100
    nps_score = promoters_percent - detractors_percent
    return f"{nps_score:.2f}"


def plot_nps_vs_reason_group_heatmap_grouped_level1(res_df, insurance_type):
    st.write("")
    reason_group_display = 'Promoting Reasons'
    if insurance_type == 'Thirdparty':
        reason_group = reasons_display_dict[reason_group_display]
        valid_columns = [col for col in thirdparty_final_reasons_dict_list[reason_group] if col in res_df.columns]
        valid_columns = valid_columns + ['score']
        if 'Problem' in reason_group_display:
            res_df = res_df[res_df['score'] < 7]
        elif 'Problem' not in reason_group_display:
            res_df = res_df[res_df['score'] > 8]

        res_df2 = res_df[valid_columns]
        reason_cols = res_df2.drop('score', axis=1).columns
    else:
        reason_group = reasons_display_dict[reason_group_display]
        valid_columns = [col for col in carbody_final_reasons_dict_list[reason_group] if col in res_df.columns]
        valid_columns = valid_columns + ['score']
        if 'Problem' in reason_group_display:
            res_df = res_df[res_df['score'] < 7]
        elif 'Problem' not in reason_group_display:
            res_df = res_df[res_df['score'] > 8]

        res_df2 = res_df[valid_columns]
        reason_cols = res_df2.drop('score', axis=1).columns

    reshaped_columns = [get_display(arabic_reshaper.reshape(col)) for col in reason_cols]
    heatmap_data = res_df2[reason_cols].sum().transpose()

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(reshaped_columns, heatmap_data, color="dodgerblue")
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    persian_font = font_manager.FontProperties(fname='Vazir-Thin.ttf')
    ax.set_yticklabels(reshaped_columns, fontproperties=persian_font, rotation=0)

    st.pyplot(fig)


def plot_nps_vs_reason_group_heatmap_grouped_level2(res_df, reason_group_display):
    st.markdown("""
        <style>
            .stSelectbox select {
                font-family: 'Vazirmatn', sans-serif;
                font-size: 16px;
            }
        </style>
    """, unsafe_allow_html=True)
    st.write("")
    reason_group = reasons_display_dict[reason_group_display]
    if ins_type == 'Thirdparty':
        valid_columns = [col for col in thirdparty_final_reasons_dict_list[reason_group] if col in res_df.columns]
    else:
        valid_columns = [col for col in carbody_final_reasons_dict_list[reason_group] if col in res_df.columns]
    valid_columns = valid_columns + ['score']
    if 'Problems' in reason_group_display:
        res_df = res_df[res_df['score'] < 7]
    elif 'Problem' not in reason_group_display:
        res_df = res_df[res_df['score'] > 8]
    res_df2 = res_df[valid_columns]
    reason_cols = res_df2.drop('score', axis=1).columns

    reshaped_columns = [get_display(arabic_reshaper.reshape(col)) for col in reason_cols]
    fig, ax = plt.subplots(figsize=(14, 10))
    heatmap_data = res_df2.groupby('score')[reason_cols].sum().transpose()
    mask = (heatmap_data == 0)

    dodgerblue_cmap = LinearSegmentedColormap.from_list("dodgerblue", ["white", "dodgerblue"])

    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap=dodgerblue_cmap, linewidths=0.5,
                ax=ax, mask=mask, center=0, cbar=False)

    ax.set_title(" ", fontsize=16)
    ax.set_xlabel(" ", fontsize=12)
    ax.set_ylabel(" ", fontsize=12)

    persian_font = font_manager.FontProperties(fname='Vazir-Thin.ttf')
    ax.set_yticks(range(len(reshaped_columns)))
    ax.set_yticklabels(reshaped_columns, rotation=0, fontproperties=persian_font)

    st.pyplot(fig)


def plot_nps_vs_reason_group_heatmap_all(res_df, insurance_type):
    if insurance_type == 'thirdparty':
        res_df = res_df[res_df['score'] < 7]
        excluded_keys = ['main_suggesting_reason']
        specific_keys = [key for key in thirdparty_final_reasons_dict_list.keys() if key not in excluded_keys]
        res_df2 = res_df.drop(['tracking_code', 'start_date', 'gregorian_start_date',
                               'period', 'jalali_period', 'سایر', 'سایر دلایل'], axis=1, errors='ignore')

        reason_cols = res_df2.columns
        summed_values_dict = {}

        filtered_dict = {key: thirdparty_final_reasons_dict_list[key] for key in specific_keys if
                         key in thirdparty_final_reasons_dict_list}

    else:
        res_df = res_df[res_df['score'] < 7]
        excluded_keys = ['main_suggesting_reason']
        specific_keys = [key for key in carbody_final_reasons_dict_list.keys() if key not in excluded_keys]
        res_df2 = res_df.drop(['tracking_code', 'start_date', 'gregorian_start_date',
                               'period', 'jalali_period', 'سایر', 'سایر دلایل'], axis=1, errors='ignore')

        reason_cols = res_df2.columns
        summed_values_dict = {}

        filtered_dict = {key: carbody_final_reasons_dict_list[key] for key in specific_keys if
                         key in carbody_final_reasons_dict_list}
    for key, columns in filtered_dict.items():
        existing_columns = [col for col in columns if col in reason_cols]
        total_sum = res_df2[existing_columns].sum().sum()
        summed_values_dict[key] = total_sum
    sorted_items = sorted(summed_values_dict.items(), key=lambda item: item[1], reverse=True)

    sorted_keys = [item[0] for item in sorted_items]
    sorted_values = [item[1] for item in sorted_items]

    labels = [get_key_by_value(reasons_display_dict, key) for key in sorted_keys]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(sorted_keys, sorted_values, color='dodgerblue')
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    persian_font = font_manager.FontProperties(fname='Vazir-Thin.ttf')
    ax.set_yticklabels(labels, fontproperties=persian_font, rotation=0)

    st.pyplot(fig)


def score_trend(res_df):
    conditions = [
        res_df['score'].isin([9, 10]),
        res_df['score'].between(7, 8),
        res_df['score'] < 7
    ]

    nps_groups = ['promoter', 'passive', 'detractor']

    res_df['nps_group'] = np.select(conditions, nps_groups, default='unknown')

    res_df['gregorian_start_date'] = res_df['start_date'].apply(convert_jalali_to_gregorian)

    res_df = get_jalali_period(res_df)

    score_counts = res_df.groupby(['jalali_period', 'nps_group']).size().unstack().fillna(0)
    score_percentages = score_counts.div(score_counts.sum(axis=1), axis=0) * 100

    total_counts = score_counts.sum(axis=1)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    score_percentages.plot(ax=ax1, color=['Teal', 'PowderBlue', 'dodgerblue', 'lightsalmon'],
                           marker='o', linewidth=4)

    ax1.set_title(' ')
    ax1.set_xlabel(' ')
    ax1.set_ylabel('Percentage (%)')

    ax2 = ax1.twinx()

    total_counts.plot.bar(ax=ax2, color='gray', alpha=0.3, width=0.3, position=1)

    ax2.set_ylabel('Total Count')

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    # ax2.spines['right'].set_visible(False)

    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    ax2.xaxis.set_ticks_position('bottom')
    ax2.yaxis.set_ticks_position('right')

    ax1.legend(loc='upper left', frameon=False, edgecolor='none')
    # ax2.legend(title='Total Count', loc='upper right', frameon=False, edgecolor='none')

    plt.subplots_adjust(right=1.5, bottom=0.2)

    plt.show()
    st.pyplot(fig)


def stacked_visualize_reasons_main(res_df, insurance_type, n):
    if insurance_type == 'Thirdparty':
        reason_group_display = 'Promoting Reasons'
        reason_group = reasons_display_dict[reason_group_display]

        valid_columns = [col for col in thirdparty_final_reasons_dict_list[reason_group] if
                         col in thirdparty_df.columns]

    if insurance_type == 'Carbody':
        reason_group_display = 'Promoting Reasons'
        reason_group = reasons_display_dict[reason_group_display]
        valid_columns = [col for col in carbody_final_reasons_dict_list[reason_group] if col in carbody_df.columns]

    res_df['gregorian_start_date'] = res_df['start_date'].apply(convert_jalali_to_gregorian)
    res_df['gregorian_start_date'] = pd.to_datetime(res_df['gregorian_start_date'])
    res_df = get_jalali_period(res_df)
    persian_font = font_manager.FontProperties(fname='Vazir-Thin.ttf')
    valid_columns = valid_columns + ['start_date'] + ['jalali_period']
    res_df = res_df[valid_columns]
    count_ones = {}
    for c in res_df.columns:
        if c not in ['tracking_code', 'start_date', 'score',
                     'period', 'gregorian_start_date', 'jalali_period']:
            count_ones[c] = res_df[c].sum()
    sorted_counts = dict(sorted(count_ones.items(), key=lambda item: item[1], reverse=True))
    top_columns = list(sorted_counts.keys())[:n]

    weekly_data = res_df.groupby('jalali_period')[top_columns].sum()

    weekly_data_percent = weekly_data.div(weekly_data.sum(axis=1), axis=0) * 100

    weekly_sum = weekly_data[top_columns].sum(axis=1)

    reshaped_columns = [get_display(arabic_reshaper.reshape(col)) for col in top_columns]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    weekly_data_percent.plot(kind='bar', stacked=True, ax=ax1,
                             cmap="YlGn",
                             edgecolor='none')
    ax1.set_xlabel(' ')
    ax1.set_ylabel('Percentage')
    ax1.set_title(' ')
    ax1.legend(
        reshaped_columns,
        prop=persian_font,
        edgecolor='none',
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(reshaped_columns),
        frameon=False
    )
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.xticks()

    ax2 = ax1.twinx()
    weekly_data.index = weekly_data.index.map(str)
    ax2.plot(weekly_data.index, weekly_sum, color='black', marker='o',
             linewidth=4)
    ax2.set_ylabel('Total Count')
    ax2.spines['top'].set_visible(False)
    ax2.legend(loc="upper left", frameon=False)
    plt.subplots_adjust(right=1.5, bottom=0.2)
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    ax2.yaxis.set_ticks_position('right')
    plt.tight_layout()
    st.pyplot(fig)


def stacked_visualize_reasons_level2(res_df, n, reason_group_display):
    reason_group = reasons_display_dict[reason_group_display]
    if ins_type == 'Thirdparty':
        valid_columns = [col for col in thirdparty_final_reasons_dict_list[reason_group] if col in res_df.columns]
    else:
        valid_columns = [col for col in carbody_final_reasons_dict_list[reason_group] if
                         col in res_df.columns]

    res_df['gregorian_start_date'] = res_df['start_date'].apply(convert_jalali_to_gregorian)
    res_df['gregorian_start_date'] = pd.to_datetime(res_df['gregorian_start_date'])

    res_df = get_jalali_period(res_df)
    persian_font = font_manager.FontProperties(fname='Vazir-Thin.ttf')
    valid_columns = valid_columns + ['start_date'] + ['jalali_period']
    res_df = res_df[valid_columns]
    count_ones = {}
    for c in res_df.columns:
        if c not in ['tracking_code', 'start_date', 'score', 'gregorian_start_date', 'jalali_period']:
            count_ones[c] = res_df[c].sum()
    sorted_counts = dict(sorted(count_ones.items(), key=lambda item: item[1], reverse=True))
    top_columns = list(sorted_counts.keys())[:n]

    weekly_data = res_df.groupby('jalali_period')[top_columns].sum()

    weekly_data = weekly_data.groupby('jalali_period')[top_columns].sum()

    weekly_data_percent = weekly_data.div(weekly_data.sum(axis=1), axis=0) * 100

    weekly_sum = weekly_data[top_columns].sum(axis=1)

    reshaped_columns = [get_display(arabic_reshaper.reshape(col)) for col in top_columns]

    fig, ax1 = plt.subplots(figsize=(16, 11))

    dodgerblue_cmap = LinearSegmentedColormap.from_list("Red", ["lightsalmon", "Red"])
    weekly_data_percent.plot(kind='bar', stacked=True, ax=ax1,
                             cmap=dodgerblue_cmap,
                             edgecolor='none')
    ax1.set_xlabel(' ')
    ax1.set_ylabel('Percentage')
    ax1.set_title(' ')
    ax1.legend(
        reshaped_columns,
        prop=persian_font,
        edgecolor='none',
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(reshaped_columns),
        frameon=False
    )
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.xticks()

    ax2 = ax1.twinx()
    # ax2.plot(weekly_data.index, weekly_sum, color='black', marker='o',
    #          linewidth=4)
    weekly_data.index = weekly_data.index.map(str)
    ax2.plot(weekly_data.index, weekly_sum, color='black', marker='o', linewidth=4)

    ax2.set_ylabel('Total Count')
    ax2.spines['top'].set_visible(False)
    ax2.legend(loc="upper left", frameon=False)
    plt.subplots_adjust(right=1.5, bottom=0.2)
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    ax2.yaxis.set_ticks_position('right')
    plt.tight_layout()
    st.pyplot(fig)


def bars_visualize_reasons_grouped(res_df, n):
    st.write(res_df.columns)
    persian_font = font_manager.FontProperties(fname='Vazir-Thin.ttf')
    res_df['nps_group'] = res_df['score'].apply(
        lambda x: 'detractor' if x < 7 else ('neutral' if x < 9 else 'promoter'))
    res_df['gregorian_start_date'] = res_df['start_date'].apply(convert_jalali_to_gregorian)
    res_df['gregorian_start_date'] = pd.to_datetime(res_df['gregorian_start_date'])

    if aggregation_level == "Weekly":
        res_df['period'] = res_df['gregorian_start_date'].dt.to_period('W').dt.start_time
    elif aggregation_level == "Monthly":
        res_df['period'] = res_df['gregorian_start_date'].dt.to_period('M').dt.start_time
    elif aggregation_level == "Seasonally":
        res_df['period'] = res_df['gregorian_start_date'].dt.to_period('Q').dt.start_time

    count_ones = {}
    for c in res_df.columns:
        if c not in ['tracking_code', 'start_date', 'score', 'period', 'gregorian_start_date', 'nps_group']:
            count_ones[c] = res_df[c].sum()

    sorted_counts = dict(sorted(count_ones.items(), key=lambda item: item[1], reverse=True))
    top_columns = list(sorted_counts.keys())[:n]

    grouped_data = res_df.groupby(['nps_group'])[top_columns].sum()
    grouped_data = grouped_data[top_columns]

    reshaped_columns = [get_display(arabic_reshaper.reshape(col)) for col in top_columns]

    nps_groups = grouped_data.index.tolist()
    x = range(len(nps_groups))
    bar_width = 0.2

    fig, ax = plt.subplots(figsize=(12, 8))

    for i, column in enumerate(top_columns):
        ax.bar([pos + i * bar_width for pos in x], grouped_data[column], bar_width, label=reshaped_columns[i])

    ax.set_xlabel('NPS Groups')
    ax.set_ylabel('Count')
    ax.set_title('Top Reasons by NPS Group')
    ax.set_xticks([pos + bar_width * (len(top_columns) / 2 - 0.5) for pos in x])
    ax.set_xticklabels(nps_groups)
    ax.legend(prop=persian_font, loc='best')
    plt.tight_layout()
    st.pyplot(fig)


def get_jalali_period_business(integrated_data):
    integrated_data['paid_date_day'] = pd.to_datetime(integrated_data['paid_date_day'])
    periods = []

    for date in integrated_data['paid_date_day']:
        jalali_date = JalaliDate.to_jalali(date)
        if aggregation_level == "Weekly":
            start_of_week = jalali_date - pd.Timedelta(days=jalali_date.weekday() + 1)
            periods.append(start_of_week)
        elif aggregation_level == "Monthly":
            start_of_month = JalaliDate(jalali_date.year, jalali_date.month, 1)
            periods.append(start_of_month)
        elif aggregation_level == "Seasonally":
            start_month = 1 + 3 * ((jalali_date.month - 1) // 3)
            start_of_quarter = JalaliDate(jalali_date.year, start_month, 1)
            periods.append(start_of_quarter)

    integrated_data['jalali_period'] = periods
    return integrated_data


def plot_thirdparty_sla(integrated_data):
    integrated_data = get_jalali_period_business(integrated_data)
    aggregated_data = integrated_data.groupby('jalali_period').agg({
        'bb_redline_sla_counts': 'sum',
        'thirdparty_bb_order_count': 'sum'
    }).reset_index()

    aggregated_data['percentage'] = (
            aggregated_data['bb_redline_sla_counts'] /
            aggregated_data['thirdparty_bb_order_count'] * 100
    )

    aggregated_data['jalali_period_str'] = aggregated_data['jalali_period'].apply(
        lambda x: f"{x.year}-{x.month:02d}-{x.day:02d}"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        aggregated_data['jalali_period_str'],
        aggregated_data['percentage'],
        marker='o', label='Percentage', linewidth=4, color='MediumSeaGreen'
    )

    for i, row in aggregated_data.iterrows():
        ax.annotate(
            f"{row['percentage']:.1f}%",
            (row['jalali_period_str'], row['percentage']),
            textcoords="offset points", xytext=(0, 10),
            ha='center', fontsize=10, color='MediumSeaGreen'
        )

    ax.set_title('')
    ax.set_xlabel(' ')
    ax.set_ylabel('Percentage')
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)


def plot_carbody_sla(integrated_data):
    integrated_data = get_jalali_period_business(integrated_data)
    aggregated_data = integrated_data.groupby('jalali_period').agg({
        'carbody_48hours': 'sum',
        'total_carbody_count': 'sum'
    }).reset_index()

    aggregated_data['percentage'] = (
            aggregated_data['carbody_48hours'] /
            aggregated_data['total_carbody_count'] * 100
    )

    aggregated_data['jalali_period_str'] = aggregated_data['jalali_period'].apply(
        lambda x: f"{x.year}-{x.month:02d}-{x.day:02d}"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        aggregated_data['jalali_period_str'],
        aggregated_data['percentage'],
        marker='o', label='Percentage', linewidth=4, color='MediumSeaGreen'
    )

    for i, row in aggregated_data.iterrows():
        ax.annotate(
            f"{row['percentage']:.1f}%",
            (row['jalali_period_str'], row['percentage']),
            textcoords="offset points", xytext=(0, 10),
            ha='center', fontsize=10, color='MediumSeaGreen'
        )

    ax.set_title('')
    ax.set_xlabel(' ')
    ax.set_ylabel('Percentage')
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)


def plot_cancelled_orders(integrated_data):
    # Define the aggregation level
    if aggregation_level == "Weekly":
        integrated_data['period'] = integrated_data['paid_date_day'].dt.to_period('W').dt.start_time
    elif aggregation_level == "Monthly":
        integrated_data['period'] = integrated_data['paid_date_day'].dt.to_period('M').dt.start_time
    elif aggregation_level == "Seasonally":
        integrated_data['period'] = integrated_data['paid_date_day'].dt.to_period('Q').dt.start_time
    else:
        raise ValueError("Invalid aggregation level. Choose 'Weekly', 'Monthly', or 'Seasonally'.")

    # Convert Gregorian periods to Jalali
    integrated_data['jalali_period'] = integrated_data['period'].apply(convert_gregorian_to_jalali)

    # Aggregation for Thirdparty
    thirdparty_data = integrated_data.groupby('jalali_period').agg({
        'thirdparty_cancelled_count': 'sum',
        'total_thirdparty_count': 'sum'
    }).reset_index()
    thirdparty_data['percentage'] = (
            thirdparty_data['thirdparty_cancelled_count'] /
            thirdparty_data['total_thirdparty_count'] * 100
    )

    # Aggregation for Carbody
    carbody_data = integrated_data.groupby('jalali_period').agg({
        'carbody_cancelled_count': 'sum',
        'total_carbody_count': 'sum'
    }).reset_index()
    carbody_data['percentage'] = (
            carbody_data['carbody_cancelled_count'] /
            carbody_data['total_carbody_count'] * 100
    )

    # Merge data for consistent periods
    combined_data = pd.merge(
        thirdparty_data[['jalali_period', 'percentage']],
        carbody_data[['jalali_period', 'percentage']],
        on='jalali_period',
        suffixes=('_thirdparty', '_carbody')
    )

    # Plot the combined data
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        combined_data['jalali_period'],
        combined_data['percentage_thirdparty'],
        marker='o', label='Thirdparty Insurance', linewidth=2, color='dodgerblue'
    )
    ax.plot(
        combined_data['jalali_period'],
        combined_data['percentage_carbody'],
        marker='o', label='Carbody Insurance', linewidth=2, color='MediumSeaGreen'
    )

    # Annotate points
    for i, row in combined_data.iterrows():
        ax.annotate(
            f"{row['percentage_thirdparty']:.1f}%",
            (row['jalali_period'], row['percentage_thirdparty']),
            textcoords="offset points", xytext=(0, 10),
            ha='center', fontsize=10, color='dodgerblue'
        )
        ax.annotate(
            f"{row['percentage_carbody']:.1f}%",
            (row['jalali_period'], row['percentage_carbody']),
            textcoords="offset points", xytext=(0, -15),
            ha='center', fontsize=10, color='MediumSeaGreen'
        )

    # Customize the chart
    ax.set_title('')
    ax.set_xlabel(' ')
    ax.set_ylabel(' ')
    ax.set_yticks([])
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.legend(frameon=False)

    plt.tight_layout()
    st.pyplot(fig)


# def stacked_visualize_reasons_business(integrated_data, insurance_type):
#     if insurance_type == 'Thirdparty':
#         time_categories = ['less_than_12_hours_thirdparty', 'less_than_24_hours_thirdparty',
#                            'less_than_48_hours_thirdparty',
#                            'less_than_120_hours_thirdparty', 'more_than_120_hours_thirdparty']
#     else:
#         time_categories = ['less_than_12_hours_carbody', 'less_than_24_hours_carbody',
#                            'less_than_48_hours_carbody',
#                            'less_than_120_hours_carbody', 'more_than_120_hours_carbody']
#
#     required_columns = ['jalali_period'] + time_categories
#     integrated_data = get_jalali_period_business(integrated_data)
#     integrated_data = integrated_data[required_columns]
#
#     weekly_data = integrated_data.groupby('jalali_period')[time_categories].sum()
#
#     weekly_data_percent = weekly_data.div(weekly_data.sum(axis=1), axis=0) * 100
#
#     # reshaped_columns = [get_display(arabic_reshaper.reshape(col)) for col in time_categories]
#
#     fig, ax1 = plt.subplots(figsize=(12, 6))
#
#     weekly_data_percent.plot(kind='bar', stacked=True, ax=ax1,
#                              color=['dodgerblue', 'skyblue', 'honeydew', 'lemonchiffon', 'lightsalmon'],
#                              edgecolor='none')
#
#     ax1.set_xlabel(' ')
#     ax1.set_ylabel('Percentage')
#     ax1.set_title(' ')
#     labels = ['Less Than 12 Hours', 'Less Than 24 Hours', 'Less Than 48 Hours',
#               'Less Than 120 Hours', 'More Than 120 Hours']
#     ax1.legend(labels, prop=font_manager.FontProperties(fname='Vazir-Thin.ttf'), edgecolor='none',
#                loc='upper center',
#                bbox_to_anchor=(0.5, 1.15), ncol=len(labels), frameon=False)
#
#     ax1.spines['top'].set_visible(False)
#     ax1.spines['right'].set_visible(False)
#     ax1.grid(False)
#
#     ax2 = ax1.twinx()
#
#     weekly_sum = weekly_data.sum(axis=1)
#     weekly_data.index = weekly_data.index.map(str)
#
#     ax2.plot(weekly_data.index, weekly_sum, color='black', marker='o', linewidth=4)
#     ax2.set_ylabel('Total Count')
#     ax2.spines['top'].set_visible(False)
#     ax2.legend(loc="upper left", frameon=False)
#
#     plt.subplots_adjust(right=1.5, bottom=0.2)
#     ax1.xaxis.set_ticks_position('bottom')
#     ax1.yaxis.set_ticks_position('left')
#     ax2.yaxis.set_ticks_position('right')
#
#     plt.tight_layout()
#     st.pyplot(fig)


def plot_login_success_rate(login_data):
    login_data['attempts_week_start'] = pd.to_datetime(login_data['attempts_week_start'])
    login_data['paid_date_day'] = login_data['attempts_week_start'].dt.date
    login_data['paid_date_day'] = pd.to_datetime(login_data['paid_date_day'])
    gregorian_start_date = convert_jalali_to_gregorian(start_date)
    gregorian_end_date = convert_jalali_to_gregorian(end_date)
    login_data = login_data[(login_data['paid_date_day'] >= gregorian_start_date) & (
            login_data['paid_date_day'] <= gregorian_end_date)]

    login_data = get_jalali_period_business(login_data)
    aggregated_data = login_data.groupby('jalali_period').agg({
        'success_count': 'sum',
        'counter': 'sum'
    }).reset_index()

    aggregated_data['success_rate'] = (
            aggregated_data['success_count'] /
            aggregated_data['counter'] * 100
    )

    aggregated_data['jalali_period_str'] = aggregated_data['jalali_period'].apply(
        lambda x: f"{x.year}-{x.month:02d}-{x.day:02d}"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        aggregated_data['jalali_period_str'],
        aggregated_data['success_rate'],
        marker='o', label='Success Rate', linewidth=4, color='MediumSeaGreen'
    )

    for i, row in aggregated_data.iterrows():
        ax.annotate(
            f"{row['success_rate']:.1f}%",
            (row['jalali_period_str'], row['success_rate']),
            textcoords="offset points", xytext=(0, 10),
            ha='center', fontsize=10, color='MediumSeaGreen'
        )

    ax.set_title('')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_yticks([])
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)


def filter_business_data(integrated_data, start_date, end_date):
    gregorian_start_date = convert_jalali_to_gregorian(start_date)
    gregorian_end_date = convert_jalali_to_gregorian(end_date)
    integrated_data['paid_date_day'] = integrated_data['paid_date_day'].astype(str).str[:19]
    integrated_data['paid_date_day'] = pd.to_datetime(integrated_data['paid_date_day'], errors='coerce')
    return integrated_data[
            (integrated_data['paid_date_day'] >= gregorian_start_date) &
            (integrated_data['paid_date_day'] <= gregorian_end_date)
            ]


with st.sidebar:
    st.header("")
    start_date = st.text_input("Start Date (YYYY/MM/DD):", "1403/01/01")
    end_date = st.text_input("End Date (YYYY/MM/DD):", "1403/12/29")
    ins_type = 'Thirdparty'
    aggregation_level = st.selectbox("Select Aggregation Level:", ["Monthly", "Seasonally"],
                                     key='agg_key')

overall_integrated_data = fetch_metabase_data()
# overall_integrated_data['paid_date_day'] = pd.to_datetime(overall_integrated_data['paid_date_day'])
final_business_data = filter_business_data(overall_integrated_data, start_date, end_date)

try:
    nps_file = pd.read_csv('data/output.csv')
    thirdparty_nps_file = fetch_gsheet_data()
    carbody_nps_file = pd.read_csv('data/output_carbody.csv')

    thirdparty_df = create_pivot_table(thirdparty_nps_file, start_date, end_date, 'thirdparty')
    thirdparty_df['سایر'] = 0
    thirdparty_df['سایر دلایل'] = 0
    thirdparty_df.to_csv('test.csv', index=False)


except Exception as e:
    st.error(f"An error occurred: {e}")


def empty_chart():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks([])
    st.pyplot(fig)


st.markdown("""
    <style>
        .stSelectbox select {
            font-family: 'Vazirmatn', sans-serif;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>NPS Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Ordibehesht 1403 untill now</h4>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>NPS Segment Share Trend</h4>", unsafe_allow_html=True)
if ins_type == 'Thirdparty':
    score = calculate_nps_score(thirdparty_df)
    st.markdown(f"<h4 style='text-align: center;'>NPS: {score}</h4>", unsafe_allow_html=True)
    score_trend(thirdparty_df)
else:
    score = calculate_nps_score(carbody_df)
    st.markdown(f"<h4 style='text-align: center;'>NPS: {score}</h4>", unsafe_allow_html=True)
    score_trend(carbody_df)

if ins_type == 'Thirdparty':
    st.markdown("<h4 style='text-align: center;'>Share of Each Thirdparty Suggesting Reasons</h4>",
                unsafe_allow_html=True)
    stacked_visualize_reasons_main(thirdparty_df, ins_type, 5)
else:
    st.markdown("<h4 style='text-align: center;'>Share of Each Carbody Suggesting Reasons</h4>",
                unsafe_allow_html=True)
    stacked_visualize_reasons_main(carbody_df, ins_type, 5)

col13, col14 = st.columns(2)
with col13:
    st.markdown("<h4 style='text-align: right;'>Promoters Main Reasons by NPS Score</h4>",
                unsafe_allow_html=True)
    if ins_type == 'Thirdparty':
        plot_nps_vs_reason_group_heatmap_grouped_level1(thirdparty_df, ins_type)
    else:
        plot_nps_vs_reason_group_heatmap_grouped_level1(carbody_df, ins_type)
with col14:
    st.markdown("<h4 style='text-align: center;'>Detractors Main Reasons</h4>",
                unsafe_allow_html=True)
    if ins_type == 'Thirdparty':
        plot_nps_vs_reason_group_heatmap_all(thirdparty_df, 'thirdparty')
    else:
        plot_nps_vs_reason_group_heatmap_all(carbody_df, 'carbody')

# rgd = st.selectbox('', list(['Issuance Problems',
#                              'CallCenter Problems',
#                              'Website Problems',
#                              'Payment Problems']), key='selectbox_1')
st.write("")
st.markdown("<h3 style='text-align: center;'>Issuance</h3>", unsafe_allow_html=True)
col15, col16 = st.columns(2)
with col15:
    st.write("")
    st.markdown("<h4 style='text-align: center;'>Detractors Secondary Reasons</h4>", unsafe_allow_html=True)
    st.write("")
    if ins_type == 'Thirdparty':
        stacked_visualize_reasons_level2(thirdparty_df, 5, reason_group_display="Issuance Problems")
    else:
        stacked_visualize_reasons_level2(carbody_df, 5, reason_group_display="Issuance Problems")
with col16:
    st.write("")
    st.markdown("<h4 style='text-align: right;'>Detractors Secondary Reasons By Score</h4>", unsafe_allow_html=True)
    if ins_type == 'Thirdparty':
        plot_nps_vs_reason_group_heatmap_grouped_level2(thirdparty_df, reason_group_display="Issuance Problems")
    else:
        plot_nps_vs_reason_group_heatmap_grouped_level2(carbody_df, reason_group_display="Issuance Problems")
col7, col8 = st.columns(2)
with col7:
    st.markdown("<h4 style='text-align: center;'>Thirdparty SLA Met Shares</h4>", unsafe_allow_html=True)
    plot_thirdparty_sla(final_business_data)
with col8:
    st.markdown("<h4 style='text-align: center;'>Carbody SLA Met Share</h4>", unsafe_allow_html=True)
    plot_carbody_sla(final_business_data)

# st.markdown("<h4 style='text-align: center;'>Share of Issuance Time Range</h4>", unsafe_allow_html=True)
# stacked_visualize_reasons_business(final_business_data, ins_type)

st.markdown("<h3 style='text-align: center;'>CallCenter</h3>", unsafe_allow_html=True)
col20, col21 = st.columns(2)
with col20:
    st.write("")
    st.markdown("<h4 style='text-align: center;'>Detractors Secondary Reasons</h4>", unsafe_allow_html=True)
    st.write("")
    if ins_type == 'Thirdparty':
        stacked_visualize_reasons_level2(thirdparty_df, 5, reason_group_display="CallCenter Problems")
    else:
        stacked_visualize_reasons_level2(carbody_df, 5, reason_group_display="CallCenter Problems")
with col21:
    st.write("")
    st.markdown("<h4 style='text-align: right;'>Detractors Secondary Reasons By Score</h4>", unsafe_allow_html=True)
    if ins_type == 'Thirdparty':
        plot_nps_vs_reason_group_heatmap_grouped_level2(thirdparty_df, reason_group_display="CallCenter Problems")
    else:
        plot_nps_vs_reason_group_heatmap_grouped_level2(carbody_df, reason_group_display="CallCenter Problems")
st.markdown("<h3 style='text-align: center;'>Website</h3>", unsafe_allow_html=True)
col22, col23 = st.columns(2)
with col22:
    st.write("")
    st.markdown("<h4 style='text-align: center;'>Detractors Secondary Reasons</h4>", unsafe_allow_html=True)
    st.write("")
    if ins_type == 'Thirdparty':
        stacked_visualize_reasons_level2(thirdparty_df, 5, reason_group_display="Website Problems")
    else:
        stacked_visualize_reasons_level2(carbody_df, 5, reason_group_display="Website Problems")
with col23:
    st.write("")
    st.markdown("<h4 style='text-align: right;'>Detractors Secondary Reasons By Score</h4>", unsafe_allow_html=True)
    if ins_type == 'Thirdparty':
        plot_nps_vs_reason_group_heatmap_grouped_level2(thirdparty_df, reason_group_display="Website Problems")
    else:
        plot_nps_vs_reason_group_heatmap_grouped_level2(carbody_df, reason_group_display="Website Problems")
st.markdown("<h3 style='text-align: center;'>Payment</h3>", unsafe_allow_html=True)
col24, col25 = st.columns(2)
with col24:
    st.write("")
    st.markdown("<h4 style='text-align: center;'>Detractors Secondary Reasons</h4>", unsafe_allow_html=True)
    st.write("")
    if ins_type == 'Thirdparty':
        stacked_visualize_reasons_level2(thirdparty_df, 5, reason_group_display="Payment Problems")
    else:
        stacked_visualize_reasons_level2(carbody_df, 5, reason_group_display="Payment Problems")
with col25:
    st.write("")
    st.markdown("<h4 style='text-align: right;'>Detractors Secondary Reasons By Score</h4>", unsafe_allow_html=True)
    if ins_type == 'Thirdparty':
        plot_nps_vs_reason_group_heatmap_grouped_level2(thirdparty_df, reason_group_display="Payment Problems")
    else:
        plot_nps_vs_reason_group_heatmap_grouped_level2(carbody_df, reason_group_display="Payment Problems")

st.write("")
st.markdown("<h3 style='text-align: center;'>Call Center</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>AVG Call Waiting Time"
            "Time</h4>", unsafe_allow_html=True)
empty_chart()
col11, col12 = st.columns(2)
with col11:
    st.markdown("<h4 style='text-align: center;'>FCR Time</h4>", unsafe_allow_html=True)
    empty_chart()
with col12:
    st.markdown("<h4 style='text-align: center;'>Call Quality Score"
                "Time</h4>", unsafe_allow_html=True)
    empty_chart()

st.write("")
st.markdown("<h3 style='text-align: center;'>Website</h3>", unsafe_allow_html=True)
login_data = pd.read_csv('login_data.csv')
st.markdown("<h4 style='text-align: center;'>Login Success Rate</h4>", unsafe_allow_html=True)
plot_login_success_rate(login_data)
