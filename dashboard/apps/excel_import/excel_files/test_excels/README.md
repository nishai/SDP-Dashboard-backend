Files starting with "a\_" are dependancies of files starting with "b\_" and so on. i.e a\_schools has courses that need to be added to CourseInfo table when b\_ScienceFaculty has data going to other tables that use foreign keys to the CourseInfo table.
Thus files starting with "a\_" should be imported first, then files starting with "b\_" and so on (and that is how the imprt script does it)
