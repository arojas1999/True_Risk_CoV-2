"""
This program will provide the User / Patient / Practitioner with the PPV or NPV for the clinical test
administered. This data is necessary to inform accurate medical decisions and to guide behaviors that
directly affect the user and its community in the case of certain contagious diseases (e.g. SARS-CoV-2).
Runs on .csv using pandas.
Runs on .csv from url.
Provides data that matches the exact date provided by the user......!!!!
See p_csv1.py for the troubleshooting from .xlsx to .csv.
See p_csv2.py for the troubleshooting for downloading a .csv file from a url.
See p_csv3.py for code to download the .csv file that exactly matches date_user().
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import requests

# create a list with Sensitivity, Specificity for each test approved by the CDC (TODO)
ELECSYS_SENSITIVITY_1 = 0.665
ELECSYS_SENSITIVITY_2 = 0.881
ELECSYS_SENSITIVITY_3 = 1
ELECSYS_SPECIFICITY = .9981

# This code informs the user of its PPV or NPV after using the Elecsys Anti-SARS-CoV-2 test.
def main():
    date_user1 = date_user()
    covid19 = get_csv(date_user1)
    test_user()
    result_of_test = test_result()
    state_user = location_user(covid19)
    list_3 = find_numbers(covid19, state_user)
    num1 = list_3[0]
    num2 = list_3[1]
    list_6 = location_risk(num1, num2, state_user)
    num3 = list_6[0]
    num4 = list_6[1]
    risk_assestment(result_of_test, num3, num4, state_user)

# request input from user
def date_user():
    print('This program will calculate the probability of the result of your SARS-CoV-2 Test being True.')
    print('This probability is calculated based on the daily prevalence of SARS-CoV-2 in your location.')
    print('Please enter the date the Test was administered:')
    year = (int(input('Enter a year: ')))
    month = (int(input('Enter a month: ')))
    day = (int(input('Enter a day: ')))
    date_user = datetime.date(year, month, day)
    print('The date the Test was administered was ' + str(date_user))
    return date_user

# connects to the Johns Hopkins University github and gets the .csv on SARS-CoV-2 that matches the date_user.
def get_csv(date_user1):
    now = date_user1
    gh = now.strftime("%m-%d-%Y")
    gh1 = gh.replace('2020', '2020.csv')
    mock = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/05-24-2020.csv'
    mock1 = mock.replace('05-24-2020.csv', gh1)
    url = mock1
    s = requests.get(url)
    if s.status_code != 200:
        print('Your date was not found in the database.')
        exit()
    url_content = s.content
    csv_file = open(gh1, 'wb')
    csv_file.write(url_content)
    csv_file.close()
    covid19 = pd.read_csv(gh1)
    return covid19

# request name of test and provide Specificity / Sensitivity from manufacturer
def test_user():
    # selects from a group of CDC approved test (TODO)
    cdc_test = ['Elecsys', 'ABC', 'DEF']
    test_user = input('Enter the name of your test: ')
    while test_user not in cdc_test:
        print('Your test is not on the CDC approved list of tests.')
        test_user = input('Enter the name of your test: ')
        if test_user == '':
            exit()
    if test_user in cdc_test:
        print('Your test is Elecsys')
        print('The SPECIFICITY of the Elecsys Anti-SARS-CoV-2 test is: 99.81% (99.65% - 99.91%)')
        print('The SENSITIVITY of the Elecsys Anti-SARS-CoV-2 test is: 100% (88.1% - 100%)')

# Return a Positive or Negative provided by the user.
def test_result():
    accepted_results = ['Positive', 'Negative']
    test_result = (input('Enter your test result (Positive / Negative): '))
    while test_result not in accepted_results:
        print('Your answer is not a valid answer')
        test_result = (input('Enter your test result (Positive / Negative): '))
        if test_result == '':
            exit()
    if test_result in accepted_results:
        return test_result

# request location from user and print / return? prevalence
def location_user(covid19):
    state_user = (input('Enter your current location (State): '))
    state_list = covid19['Province_State'].tolist()
    while state_user not in state_list:
        print('Your State is not in the list')
        state_user = (input('Enter your current location (State): '))
        if state_user == '':
            exit()
    if state_user in state_list:
        return state_user

# Using state as input retrieves Confirmed and Incident_Rate as numeric values for further calculations.
def find_numbers(covid19, state_user):
    state_list = covid19['Province_State'].tolist()
    i = state_list.index(state_user)
    list_1 = []
    list_2 = []
    Confirmed = covid19.iloc[i, 5]
    list_1.append(Confirmed)
    Incident_Rate = covid19.iloc[i, 10]
    list_2.append(Incident_Rate)
    list_3 = list_1 + list_2
    return list_3

# Use numeric data from state to calcuate PPV and NPV
def location_risk(Confirmed, Incident_Rate, state_user):
    Prevalence = float(Incident_Rate) / 1000
    Total_Population_State_User = (Confirmed * 100) / Prevalence
    print('The prevalence in ' + str(state_user) + ' is: ' + str(Prevalence) + '%')
    pos_pos_true_positive = Confirmed * ELECSYS_SENSITIVITY_3
    pos_neg_false_positive = Confirmed - pos_pos_true_positive
    neg_neg_true_negative = (Total_Population_State_User - Confirmed) * ELECSYS_SPECIFICITY
    neg_pos_false_negative = (Total_Population_State_User - Confirmed) - neg_neg_true_negative
    list_4 = []
    list_5 = []
    a = pos_pos_true_positive
    b = neg_pos_false_negative
    c = pos_neg_false_positive
    d = neg_neg_true_negative
    PPV = (a/(a+b)) * 100
    list_4.append(PPV)
    NPV = (d/(c+d)) * 100
    list_5.append(NPV)
    list_6 = list_4 + list_5
    return list_6

# Using test_result and values for PPV and NPV inform the user on the probability of that result being true.
def risk_assestment(test_result, num3, num4, state_user):
    if test_result == 'Positive':
       print('PPV or Positive Predictive Value is the probability of your Positive test being Truly Positive.')
       print('The PPV for ' + str(state_user) + ' is: ' + str(num3) + '%')
    else:
        print('NPV or Negative Predictive Value is the probability of your Negative test being Truly Negative.')
        print('The NPV for ' + str(state_user) + ' is: ' + str(num4) + '%')

if __name__ == '__main__':
    main()
