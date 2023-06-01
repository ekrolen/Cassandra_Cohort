# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd

#import data, specify the date format, and set the default 
#"estimated availability" to False
availability_data = pd.read_csv('SalemData/calendar.csv')
availability_data['date'] = pd.to_datetime(availability_data['date']).dt.date
availability_data['true_availability'] = False

#create a set of all of the unique listing IDs
listing_identifiers = availability_data['listing_id'].unique()

#counting variables to for progress updates
total_count = listing_identifiers.size
count = 1

#iterate over each unique listing
for listing in listing_identifiers:
    print(str(count)+" of "+str(total_count))
     
    listing_availability = availability_data[availability_data['listing_id'] == listing]

    # iterate through each day for the listing
    for current_date in listing_availability['date']:
        
        # only conduct an availability calculation if the listing is availaible 
        # that night. The default value of False applies otherwise
        if listing_availability[listing_availability['date'] == 
                                current_date]['available'].values[0]=='t':
            
            # store the minimum number of nights the listing is bookable for 
            # that day
            min_stay = listing_availability[listing_availability['date'] 
                                            == current_date]['minimum_nights'].values[0]

            # if min stay is only one night, set the estiamted availability 
            # to true
            if min_stay == 1:
                idx = availability_data.index[
                    (availability_data['listing_id']==listing) & 
                    (availability_data['date'] == current_date)].tolist()
                availability_data.loc[idx,'true_availability'] = True
            else:
                available_days = 0
                
                # chech the availability from (min_stay - 1) days before the 
                # current day to (min_stay - 1) day after the current day to 
                # determine if there are min_stay days in a row where the 
                # listing is available
                for i in range(-1*(int(min_stay) - 1), int(min_stay)):
                    check_date = current_date + pd.to_timedelta(i, unit='d')
                    
                    if listing_availability[listing_availability['date'] ==
                                            check_date].size > 0:
                        if listing_availability[listing_availability['date'] ==
                                                check_date]['available'].values[0] == 't':
                            available_days = available_days + 1
                            if available_days == min_stay:
                                idx = availability_data.index[(availability_data['listing_id'] == listing) 
                                                              & (availability_data['date'] == current_date)].tolist()
                                availability_data.loc[idx,'true_availability'] = True
                                break
                        else:
                            available_days = 0                
    count = count + 1

availability_data.to_csv('SalemData/calendar_true_availability.csv', index = False)