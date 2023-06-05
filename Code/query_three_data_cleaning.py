# -*- coding: utf-8 -*-
"""
"""

import pandas as pd

# read in the listing, months, and availability data
listing_data = pd.read_csv('listings.csv')
month_data = pd.read_csv('months_salem.csv')
availability_data = pd.read_csv('calendar_true_availability.csv')

# convert dates to datetime format and create new column for year-month
availability_data['date'] = pd.to_datetime(availability_data['date'])
availability_data['month-year'] = availability_data[
    'date'].dt.strftime('%Y-%m')
month_data['year-month'] = pd.to_datetime(month_data['year-month'])
month_data['year-month'] = month_data['year-month'].dt.strftime('%Y-%m')

# eliminate unused data to minimize the size of the joined dataset
room_type = listing_data[['id', 'room_type']]
room_type.set_index('id')
availability_data = availability_data[['listing_id', 'date', 'month-year',
                                       'true_availability', 'minimum_nights']]
availability_data['date'] = pd.to_datetime(availability_data['date']).dt.date

# join the listing information to the availability information
availability_data = availability_data.join(room_type.set_index('id'),
                                           on='listing_id')

# create list of all unique listing ids
listing_ids = availability_data['listing_id'].unique()

# initialize storage for available dates
monthly_summary = []

# setup variables to display progress
list_counter = 1
total_count = listing_ids.size

# iterate through each listing
for listing in listing_ids:

    # print progress
    print(str(list_counter) + ' of ' + str(total_count))

    # create a list of all months there is data for each listing
    month_list = availability_data[availability_data['listing_id']
                                   == listing]['month-year'].unique()

    # store if each listing is a whole home or apt room type
    if availability_data[availability_data['listing_id'] ==
                         listing]['room_type'].values[0] == 'Entire home/apt':
        is_whole_home = True
    else:
        is_whole_home = False

    # iterate through each month for a given listing
    for month in month_list:

        # subset the data to only look at the monthly availability for
        # this listing
        month_availability = availability_data[availability_data['month-year']
                                               == month][availability_data
                                                         ['listing_id']
                                                         == listing]

        # initialize monthly variables
        monthly_min_night_max = -1
        day_list = []
        true_counter = 0
        current_counter = 0
        start_date = month_availability.iloc[0, 1]
        end_date = month_availability.iloc[0, 1]

        # iterate through each date
        for date in month_availability['date']:

            # stre the availability for the given date
            date_availability = month_availability[
                month_availability['date'] ==
                date]['true_availability'].values[0]

            # if the date is truely available and the previous day was
            # not available, start a stay range and increment the counter
            if date_availability and current_counter == 0:
                current_counter = current_counter + 1
                true_counter = true_counter + 1
                start_date = date

            # if the date is availalbe and the previous day was also
            # available set the date as a potential end date and
            # increment the counter
            elif date_availability and current_counter != 0:
                current_counter = current_counter + 1
                true_counter = true_counter + 1
                end_date = date

            # when the date is not available, write the range of
            # available dates to the available date list
            else:
                if current_counter == 1:
                    day_list.append(str(start_date))
                elif current_counter > 1:
                    day_list.append(str(start_date) + ' - ' + str(end_date))

                current_counter = 0

            # store the minimum number of nights for the date and
            # replace the maximum min_nights if if it larger then
            # existing maximum of ming_nights for the month
            min_nights = month_availability[month_availability['date'] ==
                                            date]['minimum_nights'].values[0]
            if min_nights > monthly_min_night_max:
                monthly_min_night_max = min_nights

        # when reaching the end of the month, still write the available days
        # to the list.
        if current_counter == 1:
            day_list.append(str(start_date))
        elif current_counter > 1:
            day_list.append(str(start_date) + ' - ' + str(end_date))

        # Calculate the percentage of days that are actually available for
        # each month (rounded to nearest 0.1%)
        availability_percent = round(true_counter/month_data[
            month_data['year-month'] == month]['total_days'].values[0], 3)

        # add the monthly summary to the output
        monthly_summary.append([listing, is_whole_home, month, day_list,
                                monthly_min_night_max, availability_percent])
    list_counter = list_counter + 1

# Convert the output to dataframe and write it to csv
output_df = pd.DataFrame(monthly_summary)
output_df.columns = ['listing_id', 'entire_home_or_apt', 'year-month',
                     'available_dates', 'min_nights',
                     'percentage_of_nights_available']
output_df.sort_values(by=['listing_id', 'year-month'])
output_df.to_csv('query3_data.csv', index=False)
