import bs4
from bs4 import BeautifulSoup
import requests
import re
import course

courses_needed_checking = ["TECHNICAL WRITING", "INTRO DIGITAL COMP ARCHITECTUR"] # Change this list to whatever
# courses you want updates on
requested_course_categories = ["EH", "CS"] # List of course categories associated with the above list


course_listings_page = requests.get("https://www.uah.edu/cgi-bin/schedule.pl?file=fall2020.html&segment=NDX")
course_listings_page_soup = bs4.BeautifulSoup(course_listings_page.text, features="html.parser")
# print(soup)

# Getting href tags for each course category
for course_category in requested_course_categories:
    course_category_links = course_listings_page_soup.find_all('a', href=re.compile("segment=" + course_category + "^."))
    print(*course_category_links, sep="\n")

# Accessing each course category
for course_category in course_category_links:
    url = "http://uah.edu" + course_category.get("href")
    course_category_page = requests.get(url)
    course_category_page_soup = bs4.BeautifulSoup(course_category_page.text, features="html.parser")
    #print(course_category_page_soup.prettify())

    #course_lines = str(course_category_page_soup.find('pre').get_text())
    #print(course_lines)
    count = 0
   # for line in course_lines.splitlines():
       # for course in courses_needed_checking:
           # if course in line: # Found a line with a course that needs checking
                #count += 1
                #print(line)
            #else:
               # count += 1
                #print(str(count) + ". " + line)
                # need to call course object creator right here'''



