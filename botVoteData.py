# generate vote data for bot
from PIL import Image, ImageDraw, ImageFont
import datetime
from bs4 import BeautifulSoup
from matplotlib.ft2font import BOLD
import requests
OrbatURL = "https://community.16aa.net/orbat/"
def main():
    # Locates the orbat and parses the content
    orbatPage = requests.get(OrbatURL)
    orbat = BeautifulSoup(orbatPage.content, "html.parser")
    calendarURL = "https://community.16aa.net/calendar/"
    calendarRAW = requests.get(calendarURL)
    operationsCalendarURL = "https://community.16aa.net/calendar/2-operations-calendar/"
    operationsCalendarRAW = requests.get(operationsCalendarURL)
    calendar = BeautifulSoup(calendarRAW.content, "html.parser")
    operationsCalendar = BeautifulSoup(operationsCalendarRAW.content, "html.parser")
    nextOpCalendarURL = operationsCalendar.find("a", {"rel":"next nofollow"})
    nextOperationsCalendarRAW = requests.get(nextOpCalendarURL["href"])
    nextOperationsCalendar = BeautifulSoup(nextOperationsCalendarRAW.content, "html.parser")

    # Sets the date range to start from today and add an arbitrary number of days to it
    def date_range():
        today = datetime.date.today()
        week = [today.strftime('%Y-%m-%d')]
        added = 0
        while added < 10:
            added += 1
            day = today + datetime.timedelta(days=added)
            week.append(day.strftime('%Y-%m-%d'))
        return week

    # Utility function that checks if the date range is beyond a single month
    def checkMonthChange(firstMonth, lastMonth):
        if firstMonth != lastMonth:
            return True
        else:
            return False

    # Receives a date range, finds all events in the operations calendar during that time period, and compiles them to present to the user
    def get_events():
        dateRange = date_range()
        based_of_today = operationsCalendar.find_all("a", {'data-ipshover-target':True})
        events = []
        for a in based_of_today:
            for i in dateRange:
                if a["data-ipshover-target"].find(i)>0:
                    events.append([i, a])
        if checkMonthChange(dateRange[0][5:7], dateRange[-1][5:7]):
            based_of_next_month = nextOperationsCalendar.find_all("a", {'data-ipshover-target':True})
            for a in based_of_next_month:
                for i in dateRange:
                    if a["data-ipshover-target"].find(i)>0:
                        events.append([i, a])
        return events



    def get_attendance_URL():
        events = get_events()
        #the first event is the first index. events[x][1]["href"] returns the x-th event available.
        return events[0][1]["href"]  

    attendanceURL = get_attendance_URL()

    # Parameter section is the id of the div displaying the members on the ORBAT ("x/y section" or similar)
    # Returns list with members in string form
    def get_section_members(section):
        full_section_selection = orbat.find(id=section)
        section_roster = full_section_selection.find_all("a")
        members = [section]
        for individual in section_roster:
            members.append(individual.text.strip())
        return members

    # Sorts all votes on chosen event into a dictionary 
    def get_voters():
        attendancePage = requests.get(attendanceURL)
        attendance = BeautifulSoup(attendancePage.content, "html.parser")
        try:
            event_title = attendance.find("h1").get_text()
            full_selection_voted_yes = attendance.find("div", id="ipsTabs_elAttendeesMob_elGoing_panel")
            full_selection_voted_maybe = attendance.find("div", id="ipsTabs_elAttendeesMob_elMaybe_panel")
            full_selection_voted_no = attendance.find("div", id="ipsTabs_elAttendeesMob_elNotGoing_panel")
            attending_voters_dirty = full_selection_voted_yes.find_all("span")
            maybe_voters_dirty = full_selection_voted_maybe.find_all("span")
            loa_voters_dirty = full_selection_voted_no.find_all("span")
            attending_voters = []
            maybe_voters = []
            loa_voters = []
            for attendee in attending_voters_dirty:
                attending_voters.append(attendee.get_text())
            for maybe in maybe_voters_dirty:
                maybe_voters.append(maybe.get_text())
            for loa in loa_voters_dirty:
                loa_voters.append(loa.get_text())
        except AttributeError as error:
            print("Make sure your URL was correct. I couldn't find anything at all there...")
            return
        votes_dictionary = {"yes": [], "maybe": [], "no": [], "title": event_title}
        for voter in attending_voters:
            votes_dictionary["yes"].append(voter)
        for voter in maybe_voters:
            votes_dictionary["maybe"].append(voter)
        for voter in loa_voters:
            votes_dictionary["no"].append(voter)
        return votes_dictionary

    # Save the votes from the event to a variable to check against with function get_attending_members()
    votes = get_voters()

    # Compares the list made from the ORBAT page with the dictionary containing the votes on the selected event
    def get_attending_members(section_list):
        section_dictionary = {"section": section_list[0], "GOING": [], "MAYBE": [], "NO": [], "NOT VOTED": []}
        for member in section_list[1:]:
            if member in votes["yes"]:
                section_dictionary["GOING"].append(member)
            elif member in votes["maybe"]:
                section_dictionary["MAYBE"].append(member)
            elif member in votes["no"]:
                section_dictionary["NO"].append(member)
            else:
                section_dictionary["NOT VOTED"].append(member)
        return section_dictionary

    # Get all the members from each section tagged with a unique ID on the ORBAT
    coyhq =  get_section_members("Coy HQ")
    oneplt = get_section_members("1 Platoon HQ")
    oneone = get_section_members("1/1 Section")
    onetwo = get_section_members("1/2 Section")
    onethree = get_section_members("1/3 Section")
    twoplt = get_section_members("2 Platoon HQ")
    twoone = get_section_members("2/1 Section")
    twotwo = get_section_members("2/2 Section")
    twothree = get_section_members("2/3 Section")
    fourplt = get_section_members("4 Platoon HQ")
    fsg = get_section_members("FSG")
    aasr = get_section_members("13AASR")
    csmr = get_section_members("16CSMR")
    jhc = get_section_members("JHC")
    fst = get_section_members("JFIST")
    sig = get_section_members("216 Sigs")
    pathfinders = get_section_members("Pathfinders")
    mi = get_section_members("3/2 Section")

    # Compile a list of the company and a variable to hold the page
    hq = [get_attending_members(coyhq), get_attending_members(oneplt), get_attending_members(twoplt), get_attending_members(fourplt)] 
    infantry = [get_attending_members(oneone), get_attending_members(onetwo), get_attending_members(onethree), get_attending_members(twoone), get_attending_members(twotwo), get_attending_members(twothree)]
    support =  [get_attending_members(fsg), get_attending_members(aasr), get_attending_members(csmr), get_attending_members(jhc), get_attending_members(fst), get_attending_members(sig), get_attending_members(pathfinders), get_attending_members(mi)]

    # uses functions to sum up the attendance for the upcoming op
    def render_attendance():
        output = Image.new("RGB",[1600,1200],color="#36393f")
        fontSpecsTitle = ImageFont.truetype("C:\Windows\Fonts\Arial.ttf",size=28)
        draw = ImageDraw.Draw(output)
        title = votes["title"].strip()
        # render OP title, followed by HQ, Infantry Plt and Support.
        draw.text((output.width/2-150, 20),title, font=fontSpecsTitle)
        output = render_sub_content(output, hq, 70)
        output = render_sub_content(output, infantry, 230)
        output = render_sub_content(output, support, 590)
        output.save("attendance.png")

    # used to write bold letters
    def draw_bold(image, text, x, y):
        fontBold = ImageFont.truetype("C:\Windows\Fonts\Ariblk.ttf", size=20)
        draw = ImageDraw.Draw(image)
        draw.text((x,y),text,font=fontBold)
        return image

    # used to write subheaders
    def draw_subheaders(image, text, x, y):
        fontSubheader = ImageFont.truetype("C:\Windows\Fonts\Arial.ttf",size=18)
        draw = ImageDraw.Draw(image)
        draw.text((x,y),text,font=fontSubheader)
        return image

    # used to write regular content
    def draw_content(image, text, x, y):
        fontRegular = ImageFont.truetype("C:\Windows\Fonts\Arial.ttf", size=14)
        draw = ImageDraw.Draw(image)
        draw.text((x,y),text,font=fontRegular)
        return image

    # compile the attendance information into an image, return said image
    def render_sub_content(image, sections, offset_y):
        offset_x = 180
        start_pos_x = (image.width - len(sections)*offset_x)/2
        row_height = 22
        original_y = offset_y
        for section in sections:
            image = draw_bold(image,section["section"], start_pos_x, original_y)
            offset_y = original_y
            offset_y += row_height + 8
            if section["GOING"] != []:
                image = draw_subheaders(image, "GOING:", start_pos_x, offset_y)
                for goer in section["GOING"]:
                    offset_y += row_height
                    image =  draw_content(image,goer, start_pos_x, offset_y)
                offset_y += row_height
            if section["MAYBE"] != []:
                image = draw_subheaders(image, "MAYBE:", start_pos_x, offset_y)
                for indecisive in section["MAYBE"]:
                    offset_y += row_height
                    image = draw_content(image,indecisive, start_pos_x, offset_y)
                offset_y += row_height
            if section["NO"] != []:
                image = draw_subheaders(image, "NO:", start_pos_x, offset_y)
                for nongoer in section["NO"]:
                    offset_y += row_height
                    image = draw_content(image,nongoer, start_pos_x, offset_y)
                offset_y += row_height
            if section["NOT VOTED"] != []:
                image = draw_subheaders(image, "NOT VOTED:", start_pos_x, offset_y)
                for non_voter in section["NOT VOTED"]:
                    offset_y += row_height
                    image = draw_content(image,non_voter, start_pos_x, offset_y)
            start_pos_x +=offset_x
        return image

    render_attendance()
main()