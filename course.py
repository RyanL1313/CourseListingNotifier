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

    def print_course(self):
        print("CRN: " + self.crn + "\nTitle: " + self.title + "\nAvailable slots: " + self.avail + "\nWaitlisted: " + self.waitlist + "\nInstructor: " + self.instructor + "\n\n")

