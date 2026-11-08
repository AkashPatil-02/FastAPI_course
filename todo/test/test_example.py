import pytest


# def test_equal_or_not():
#     assert 3==3


class Student:
    def __init__(self,first_name:str, last_name:str, major:str, years:int):
        self.first_name = first_name
        self.last_name=last_name
        self.major=major
        self.years=years


@pytest.fixture
def default_student():
    return Student('Akash','Patil','CSE',4)

def test_person_initialization(default_student):
    assert default_student.first_name=='Akash' , 'First name'
    assert default_student.last_name=='Patil' , 'Last name'
    assert default_student.major=='CSE' , 'major'
    assert default_student.years==4