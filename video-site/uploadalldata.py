import csv
import uploadmeetings
import uploadvideos
import uploadlcsh
from meetingsvideos.models import AcademicDiscipline, APSDepartment

def upload_data():
    uploadmeetings.upload_meetings()

    with open("academicdiscipline.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            discipline, created = AcademicDiscipline.objects.get_or_create(name=row["name"])
            
    with open("apsdepartment.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            discipline, created = APSDepartment.objects.get_or_create(name=row["name"])
            
    uploadvideos.upload_videos()
    
    uploadlcsh.upload_lcsh()

if __name__ == '__main__':
    upload_data()
