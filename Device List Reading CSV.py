import csv
# This version 2 (final)
def read_devices(filename="network_devices.csv"):
    t_count = 0
    with open(filename) as csvfile:  # open the csv file
        reader = csv.DictReader(csvfile)  # read by columns
        print("Reading Devices List!")
        for row in reader:
            print(row["Device Name"])
            t_count += 1 #counter for each deviece
    print(f"{t_count} Devices in the list are processed")

if __name__ == "__main__":
    read_devices() #run the function