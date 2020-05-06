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
    original_course_object_list = []  # List of course objects to be compared against the new list obtained by the
    # program

    # Obtaining the email and password before proceeding with the program
    email = input("Enter your email address: ")
    password = getpass.getpass("Enter your password: ")

    while True:
        courses_needed_checking = ["TECHNICAL WRITING", "INTRO DIGITAL COMP ARCHITECTUR"] # Change this list to whatever
        # courses you want updates on
        requested_course_categories = ["EH", "CS"] # List of course categories associated with the above list
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
                        #new_course.print_course()

                        new_course_object_list.append(new_course) # Add the course object to the new list

        if len(original_course_object_list) == 0: # First run-through of the program
            print("first run")
            original_course_object_list = copy.deepcopy(new_course_object_list) # Now we have something for comparison
        elif len(original_course_object_list) != len(new_course_object_list):  # New section was added
            print("in here")
            details_in_email.append("A new section for a course you were watching was added!")
        else: # The new and original lists are the same size. Now we just check if any course attributes have changed
            index_original = 0 # Index of original_course_object_list to be updated alongside new_course_object_list
            for course_obj in new_course_object_list:
                if course_obj != original_course_object_list[index_original]: # This course has changed
                    # Now we're checking what individual attributes changed so the e-mail will specify this
                    if course_obj.avail != original_course_object_list[index_original].avail:
                        details_in_email.append("The number of available slots for CRN " + course_obj.crn + " has "
                                                                                                            "changed.")
                    if course_obj.waitlist != original_course_object_list[index_original].waitlist:
                        details_in_email.append("The waitlist number for CRN " + course_obj.crn + " has changed.")

                    if course_obj.instructor != original_course_object_list[index_original].instructor:
                        details_in_email.append("The instructor for CRN " + course_obj.crn + " has changed.")

                    details_in_email.append("\n") # New line to separate different course sections in the e-mail

                index_original += 1

        if len(details_in_email) != 0: # There was a change to the course listings
           # email_message = create_email_message(details_in_email)  # The message that will go in the body of the email
            #send_email(email, password, email_message) # Send the email to myself about the changes
            original_course_object_list = new_course_object_list # There is now a new original list for the next comps

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
    print("in here")
    mail = smtplib.SMTP("smtp.gmail.com", 587)
    mail.ehlo()
    mail.starttls()
    mail.login(email, password)

    full_message = MIMEMultipart()

    full_message["Subject"] = "Testing"
    full_message["From"] = email
    full_message["To"] = email
    full_message.attach(MIMEText(message, "plain"))

    mail.sendmail(email, email, full_message.as_string())
    mail.close()


if __name__ == "__main__":
    main()


