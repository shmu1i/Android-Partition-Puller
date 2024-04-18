import subprocess
import re

def print_banner():
    print("Android Partition Puller")
    print("========================\n")

def list_partitions():
    # Run adb shell su -c ls -al /dev/block/by-name to list partitions
    ls_command = 'adb shell su -c ls -al /dev/block/by-name'
    ls_output = subprocess.check_output(ls_command, shell=True, text=True)

    # Extract partition names and numbers
    partitions = {}
    for line in ls_output.split('\n'):
        match = re.search(r'\s+(\w+)\s+->\s+(.*)$', line)
        if match:
            partition_name, partition_path = match.group(1), match.group(2)
            partition_number_match = re.search(r'(\d+)$', partition_path)
            if partition_number_match:
                partition_number = partition_number_match.group(1)
                partitions[int(partition_number)] = partition_name

    # Sort partitions by number
    sorted_partitions = {number: partitions[number] for number in sorted(partitions.keys())}
    return sorted_partitions

def display_partitions(partitions):
    column_width = max(len(name) for name in partitions.values()) + 5
    num_columns = 3

    for i, (number, name) in enumerate(partitions.items(), 1):
        print(f"{number}: {name.ljust(column_width)}", end="")
        if i % num_columns == 0:
            print()
    if len(partitions) % num_columns != 0:
        print()

def main():
    print_banner()

    partitions = list_partitions()

    # Print list of partitions
    print("Available partitions to pull:")
    display_partitions(partitions)

    # Ask user to choose partition(s)
    partition_numbers = input("\nEnter the number(s) of the partition(s) to pull (separated by whitespace): ").split()

    for partition_number in partition_numbers:
        try:
            partition_name = partitions[int(partition_number)]
            output_file_name = partition_name

            # Run the adb shell command to copy partition to /tmp
            adb_shell_command = f'adb shell "su -c dd if=/dev/block/by-name/{partition_name} of=/tmp/{output_file_name}"'
            print(f"\nPulling partition {partition_name}...")
            subprocess.run(adb_shell_command, shell=True, check=True)

            # Run adb pull to pull the output file from /tmp
            adb_pull_command = f'adb pull /tmp/{output_file_name}'
            subprocess.run(adb_pull_command, shell=True, check=True)
            print(f"Partition {partition_name} pulled successfully.")
        except KeyError:
            print(f"Invalid partition number: {partition_number}")

if __name__ == "__main__":
    main()
