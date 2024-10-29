# Income tax calculator
# Nick Chandler
# 10/28/2024

'''
This application reads in the agi IRS tax information, takes a location (City,State) and zipcode
and does basic analysis on the tax returns of the area.

Currently, it returns the median and mean household income tax



Data Structure:

{
    'zipcode': <zipcode-str>,
    'counts': <List of counts>,
    'lowerbounds': [1, 25000, 50000, 75000, 100000, 200000],
    'upperbounds': [24999, 49999, 74999, 99999, 199999, 10000000]
}
'''

import pandas as pd
import sys
import streamlit as st

@st.cache_data(persist='disk')
def read_df(filename):
    '''
    Wrapper for pandas read csv to allow streamlit decorator to cache data
    
    Input: filename (string)
    Output: Pandas df of csv
    '''
    return pd.read_csv(filename)


def read_in_data(zipcode, filename):
    '''
    Reads in the data and returns a dictionary 
    
    Inputs: zipcode (int), location (string), filename (string)
    Outputs: Dictionary following the structure outlined at the beginning.
    '''
    counts = []
    total = 0
    
    # Dataframe
    df_full = read_df(filename)
    
    # Clean df to be only our zip
    try:
        df = df_full[df_full['zipcode'] == int(zipcode)]
    except IndexError:
        sys.exit()
    
    # Get the totals for each of the 6 brackets
    for i in range(1, 7):  
        try:
            num_returns = float(df[df['agi_stub'] == i]['N1'].iloc[0])
        except:
            sys.exit()
        
        counts.append(num_returns)
        total += num_returns
    
    # Put it all in our raw data structure
    result = {   
        'zipcode': str(zipcode),
        'counts': counts,
        'total': total,
        'lowerbounds': [1, 25000, 50000, 75000, 100000, 200000],
        'upperbounds': [24999, 49999, 74999, 99999, 199999, 10000000]
        }
    return result



def lin_approx(x_1, y_1, x_2, y_2, x_0):
    '''
    Computes the linear approximation, y_0 of a point x_0 given two points to form the line 
    
    Inputs: points broken into x_1, y_1, x_2, y_2, and x_0 where x_0 is plugged into formula
    Outputs: y_0 = m(x_0 - x_1) + y_1 with x_0 being the middle count
    '''
    
    # Determine slope
    slope = (y_2-y_1)/(x_2-x_1)
    # Return val using formula y = m(x_0 - x_1) + y_1
    return slope*(x_0 - x_1) + y_1


def compute_mean(data_dict):
    '''
    Computes the average income for the given zip code using frequencies and midpoints of each interval

    Input: data_dict as specified at the top of the page
    Output: The average income for the given zip code
    '''
    # as one-liner??: sum([t[2]*(t[1]+t[0])/2 for t in zip(data_dict['lowerbounds'], data_dict['upperbounds'], data_dict['counts'])])/data_dict['total']
    
    numerator = 0
    endpoints_and_counts = zip(data_dict['lowerbounds'], data_dict['upperbounds'], data_dict['counts'])
    
    # Compute numerator
    for t in endpoints_and_counts:
        midpoint = (t[0] + t[1]) / 2
        numerator += t[2] * midpoint
    
    # Return average
    return numerator / data_dict['total']



def compute_median(data_dict):
    '''
    Computes the median value using linear interpolation when the middle return falls between two brackets
    
    Inputs: data_dict as specified at the top of the page
    Outputs: The median income value interpolated from the given tax bracket values, -1 if an error occurred
    '''
    bracket_number = 0
    running_total_returns = 0
    result = -1
    
    median_x = data_dict['total'] // 2
    
    
    brackets = [1, 25000, 50000, 75000, 100000, 200000, 10000000]
    for current_count in data_dict['counts']:
        running_total_returns += current_count
        if running_total_returns > median_x:
            # Compute the median 
        
            # Find the little box and record the relevant pts
            y_1 = brackets[bracket_number]
            y_2 = brackets[bracket_number + 1]
            x_1 = running_total_returns - current_count
            x_2 = running_total_returns
            
            # Do the linear approximation
            result = lin_approx(x_1, y_1, x_2, y_2, median_x)
            
            # Break tf out and return mafk
            break
        bracket_number += 1
    
    return result


def income_info(zipcode: int, filename = './Data/20zpallagi.csv'):
    '''
    Executes the core functionality of the program
    
    Inputs: zipcode (int), location (string), filename (string)
    Outputs: a tuple containing the zipcode, mean, and median income
    '''
    
    # Read our data
    data = read_in_data(zipcode, filename)
    
    # Compute the relevant statistics
    mean = compute_mean(data)
    median = compute_median(data)
    
    # Print that shit!
    print(f"The zipcode: {zipcode} has mean income: ${mean:,.2f} and median income ${median:,.2f}.")
    
    return (zipcode, mean, median)


def usage():
    '''
    Prints a helpstring for the program
    
    Inputs: None
    Outputs: None
    '''
    
    help_string = 'Usage: python3 IncomeTaxDataAnalyzer.py <zipcode> <filepath>\nExample: python3 IncomeTaxDataAnalyzer.py 98115 ./Data/20zpallagi.csv\n'
    print(help_string)
    
    
def main():
    
    st.title("Mean and Median income calculator from IRS data.")
    # Take user input
    zipcode = st.text_input("Enter a valid zipcode")
    if bool(zipcode):
        # Compute the mean and median income
        zip, mean, median = income_info(int(zipcode))
        print(mean, median)
        st.write(f"Income at zipcode {zipcode}:")
        st.write(f"Mean: \\${mean:,.2f}")
        st.write(f"Median: \\${median:,.2f}")
    
    

if __name__ == '__main__':
    main()
