# UAH Course Listing Notifier

# The purpose of this program is to notify myself via email when the status of certain attributes of UAH courses
# change. The courses to watch along with their category are defined before the infinite loop, and are necessary
# to get status updates for those courses.
# Scrapes data from the UAH public course listing page using BeautifulSoup.
# When the program is exited, the previously obtained course data is saved in savedcourses.txt, so if a change was
# made to the courses being watched on the UAH course listing page while the program wasn't running, the program will
# also be able to determine that
# Sender email and password are requested through the terminal in order to avoid putting the login information in this
# code

# Author: Ryan Lynch


import copy
import bs4
import requests
import re
from course import Course
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass


def main():
    original_course_object_list = populate_original_course_list() # Get the last saved course list from the savedcourses text file

    # Obtaining the email and password before proceeding with the program
    email = input("Enter your email address: ")
    password = getpass.getpass("Enter your password: ")

    courses_needed_checking = ["TECHNICAL WRITING", "INTRO DIGITAL COMP ARCHITECTUR"]  # Change this list to whatever
    # courses you want updates on
    requested_course_categories = ["EH", "CS"]  # List of course categories associated with the above list

    while True:
        # For debugging purposes
        for course in original_course_object_list:
            print(course.title)

        new_course_object_list = [] # New list of course objects after checking the webpage
        details_in_email = [] # List of details about what was changed on the webpage

        # The following are indexes indicating the start and end of a course's specific attribute that needs to be
        # obtained
        CRN_INDICES = (5, 11)
        TITLE_INDICES = (23, 56)
        AVAILABILE_SLOTS_INDICES = (71, 79)
        WAITLIST_INDICES = (80, 84)
        INSTRUCTOR_INDICES = (126, 155)

        course_listings_page = requests.get("https://www.uah.edu/cgi-bin/schedule.pl?file=fall2020.html&segment=NDX")
        course_listings_page_soup = bs4.BeautifulSoup(course_listings_page.text, features="html.parser")
        # print(soup)

        course_category_links = []

        # Getting href tags for each requested course category
        for course_category in requested_course_categories:
            course_category_links.append(course_listings_page_soup.find("a", href=re.compile("segment=" + course_category)))

        # Accessing each course category
        for course_category in course_category_links:
            url = "http://uah.edu" + course_category.get("href")
            course_category_page = requests.get(url)
            course_category_page_soup = bs4.BeautifulSoup(course_category_page.text, features="html.parser")

            course_lines = str(course_category_page_soup.find("pre").get_text())

            for line in course_lines.splitlines():
               for course in courses_needed_checking: # Create a course object if the course in question is on this line
                    if course in line: # Found a line with a course that needs checking
                        crn = get_course_attribute_from_line(line, CRN_INDICES)
                        course_title = get_course_attribute_from_line(line, TITLE_INDICES)
                        available_slots = get_course_attribute_from_line(line, AVAILABILE_SLOTS_INDICES)
                        waitlist_number = get_course_attribute_from_line(line, WAITLIST_INDICES)
                        instructor = get_course_attribute_from_line(line, INSTRUCTOR_INDICES)

                        # Now, create the new course object based on the acquired data
                        # Gets compared to the old course object to check if anything has changed on the webpage
                        new_course = Course(crn, course_title, available_slots, waitlist_number, instructor)
                        new_course_object_list.append(new_course) # Add the course object to the new list
        if len(original_course_object_list) != len(new_course_object_list):  # New section was added
            details_in_email.append("A new section for a course you were watching was added!\n")
        else: # The new and original lists are the same size. Now we just check if any course attributes have changed
            index_original = 0 # Index of original_course_object_list to be updated alongside new_course_object_list
            for course_obj in new_course_object_list:
                if course_obj != original_course_object_list[index_original]: # This course has changed
                    # Now we're checking what individual attributes changed so the e-mail will specify this
                    if course_obj.avail != original_course_object_list[index_original].avail:
                        details_in_email.append("The number of available slots for CRN " + course_obj.crn + " has "
                                                                                                            "changed.\n")
                    if course_obj.waitlist != original_course_object_list[index_original].waitlist:
                        details_in_email.append("The waitlist number for CRN " + course_obj.crn + " has changed.\n")

                    if course_obj.instructor != original_course_object_list[index_original].instructor:
                        details_in_email.append("The instructor for CRN " + course_obj.crn + " has changed.\n")


                index_original += 1

        if len(details_in_email) != 0: # There was a change to the course listings
            email_message = create_email_message(details_in_email)  # The message that will go in the body of the email
            send_email(email, password, email_message) # Send the email to myself about the changes

            # Create the list of information to go in the file
            new_list_to_save = create_information_to_save(new_course_object_list)
            save_course_data(new_list_to_save) # Save the new data of each course to a text file

            original_course_object_list = copy.deepcopy(new_course_object_list) # There is now a new original list for the next comps

        time.sleep(3) # This program executes every 5 minutes


# Used to retrieve a course attribute in the line of data based on the indices provided.
# The attribute is the substring obtained from the indices (2-tuple).
def get_course_attribute_from_line(line, indices):
    attribute = line[indices[0]:indices[1] + 1] # Getting the substring for the requested attribute

    return attribute.strip()


# Composes the message that gets sent in the email
# Returns the composed message
def create_email_message(details):
    message = ""
    for detail in details:
        message += detail

    return message


# Sends an email to myself about changes to UAH's course listing page
def send_email(email, password, message):
    mail = smtplib.SMTP("smtp.gmail.com", 587)
    mail.ehlo()
    mail.starttls()
    mail.login(email, password)

    full_message = MIMEMultipart()

    full_message["Subject"] = "Course Changes!"
    full_message["From"] = email
    full_message["To"] = email
    full_message.attach(MIMEText(message, "plain"))

    mail.sendmail(email, email, full_message.as_string())
    mail.close()


# Returns a list, each value in the list is a course attribute. Used to save information to the savedcourses text file.
def create_information_to_save(new_list):
    saved_list = []
    for course_obj in new_list:
        saved_list.append(course_obj.crn)
        saved_list.append(course_obj.title)
        saved_list.append(course_obj.avail)
        saved_list.append(course_obj.waitlist)
        saved_list.append(course_obj.instructor)

    return saved_list


# Write the information about each course to the savedcourses text file for use upon starting the program
def save_course_data(saved_list):
    saved_data_file = open("savedcourses.txt", "w")  # Text file that gets data for each course saved to it

    for attribute in saved_list:
        saved_data_file.write(attribute + "\n")

    saved_data_file.close()


# Puts all of the course objects into the original course list at the start of the program by reading from the
# saved data file.
# Returns the original list of courses at the start of program execution.
def populate_original_course_list():
    saved_data_file = open("savedcourses.txt", "r")  # Open saved course data text file for reading
    attributes = []
    course_list = []

    index = 0 # Used to check if a course object needs to be created and added
    for attribute in saved_data_file:
        attributes.append(attribute.strip())
        index += 1
        if index % 5 == 0: # Have all 5 of the course's attributes
            new_course = Course(attributes[0], attributes[1], attributes[2], attributes[3], attributes[4])
            course_list.append(new_course)
            attributes.clear() # Clear the list so a new course's attributes can be obtained

    saved_data_file.close()

    return course_list


if __name__ == "__main__":
    main()
