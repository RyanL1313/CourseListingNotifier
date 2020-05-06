class Course:

    def __init__(self, crn, title, avail, waitlist, instructor):
        self.crn = crn
        self.title = title
        self.avail = avail
        self.waitlist = waitlist
        self.instructor = instructor

    def __eq__(self, other):
        # These are the attributes that can change
        return other.avail == self.avail and other.waitlist == self.waitlist and other.instructor == self.instructor

    # Prints all of the course's attributes
    def print_course(self):
        print("CRN: " + self.crn + "\nTitle: " + self.title + "\nAvailable slots: " + self.avail + "\nWaitlisted: " + self.waitlist + "\nInstructor: " + self.instructor + "\n\n")

    # Writes the course data to the savedcourses text file for storage
    def put_course_data_into_text_file(self):
        saved_data_file = open("savedcourses.txt", "w")  # Text file that gets data for each course saved to it
        saved_data_file.write(self.crn + "\n" + self.title + "\n" + self.avail + "\n" + self.waitlist + "\n" + self.instructor + "\n")
        saved_data_file.close()