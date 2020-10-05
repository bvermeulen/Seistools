''' IVMS checker program
'''
import datetime
import pandas as pd
import numpy as np

IVMS_file = 'D:\\OneDrive\\Work\\PDO\\IVMS\\Daily Trip Report - IVMS.xls'
vehicle_file = 'D:\\OneDrive\\Work\\PDO\\IVMS\\Lekhwair Vehicles Demob Plan V3.xlsx'
vehicle_ivms_file = 'D:\\OneDrive\\Work\\PDO\\IVMS\\Lekhwair Vehicles - IVMS.xlsx'

class IVMS:

    def __init__(self):
        self.ivms_df = pd.read_excel(IVMS_file, header=4)
        # fill in dates where there is no date and replace the columns
        date_col = self.ivms_df['Date'].to_list()
        date_hold = pd.NaT
        for i, _date in enumerate(date_col):
            if pd.isna([_date]):
                date_col[i] = date_hold
            else:
                date_hold = _date
        self.ivms_df['Date'] = np.array(date_col)

        self.vehicle_df = pd.read_excel(vehicle_file, header=4)

        # make list of registrations from IVMS
        ivms_registration_raw = np.array(
            self.ivms_df['Asset Registration Number'].to_list())

        # make list of registrations from vehicle list
        vehicle_registrations_raw = np.array(self.vehicle_df['Reg no\n(ROP)'].to_list())

        #... and format the registrations to XXXXAA format
        self.ivms_registrations = np.array([])
        for registration in ivms_registration_raw:
            registration = ''.join([s.upper().strip() for s in registration.split()])
            self.ivms_registrations = np.append(self.ivms_registrations, registration)

        self.vehicle_registrations = np.array([])
        for registration in vehicle_registrations_raw:
            registration = ''.join([s.upper().strip() for s in registration.split()])
            self.vehicle_registrations = np.append(
                self.vehicle_registrations, registration)

    def crosscheck_with_ivms(self):
        vehicles = {
            'registration': [],
            'vehicle': [],
            'Dates IVMS': [],
            'Days in IVMS': [],
            'Last date': [],
        }

        count = 0
        for registration in self.vehicle_registrations:
            registration = ''.join([s.strip() for s in registration.upper().split()])

            # get unique list of dates where this registration is found in IVMS
            found_registrations = np.where(self.ivms_registrations == registration)[0]
            dates = sorted(list(set(
                self.ivms_df.iloc[found_registrations]['Date'].to_list())))
            days_in_ivms = len(dates)

            if days_in_ivms > 0:
                dates_str = ', '.join([d.strftime('%d-%m-%y') for d in dates])
                vehicles['registration'].append(registration)
                vehicles['vehicle'].append(self.ivms_df.iloc[found_registrations[0], 2])
                vehicles['Dates IVMS'].append(dates_str)
                vehicles['Days in IVMS'].append(days_in_ivms)
                vehicles['Last date'].append(dates[-1])

            else:
                vehicles['registration'].append(registration)
                vehicles['vehicle'].append('')
                vehicles['Dates IVMS'].append('NOT FOUND')
                vehicles['Days in IVMS'].append(days_in_ivms)
                vehicles['Last date'].append(datetime.datetime(1900, 1, 1))

                count += 1
                print(f'registration: {registration} is not found in IVMS')

        vehicle_db_ivms_df = pd.concat([self.vehicle_df, pd.DataFrame(vehicles)], axis=1)
        vehicle_db_ivms_df.to_excel(vehicle_ivms_file)
        print(f'===>>total of registrations in vehicle database not found: {count}')

    def crosscheck_with_vehicledb(self):
        # make an unique list of registrations from IVMS
        ivms_registrations = list(set(self.ivms_registrations))

        print('-'*80)
        count_found = 0
        count_not_found = 0
        for registration in ivms_registrations:
            if registration in self.vehicle_registrations:
                # print(f'registration {registration} is FOUND')
                count_found += 1

            else:
                count_not_found += 1
                print(f'===>> registration {registration} is NOT FOUND')

        print(f'total of registrations in IVMS found: {count_found}')
        print(f'total of registrations in IVMS not found: {count_not_found}')


if __name__ == '__main__':
    ivms = IVMS()
    ivms.crosscheck_with_ivms()
    ivms.crosscheck_with_vehicledb()
