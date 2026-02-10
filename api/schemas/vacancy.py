import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.enums import Currency


class VacancySalaryRangeMode(BaseModel):
    id: str
    name: str


class VacancySalaryRangeFrequency(BaseModel):
    id: str
    name: str


class VacancyMetroStation(BaseModel):
    station_name: str
    line_name: str
    station_id: str
    line_id: str
    lat: float
    lng: float


class EmployerLogoURL(BaseModel):
    original: str
    size_90: str = Field(alias="90")
    size_240: str = Field(alias="240")


class PhoneNumber(BaseModel):
    comment: str | None = None
    city: str | None = None
    number: str | None = None
    country: str
    formatted: str


class VacancyDepartment(BaseModel):
    id: str
    name: str


class VacancyArea(BaseModel):
    id: str
    name: str
    url: str


class VacancySalary(BaseModel):
    not_less: int | None = Field(default=None, alias="from")
    not_more: int | None = Field(default=None, alias="to")
    currency: Currency
    gross: bool


class VacancySalaryRange(BaseModel):
    not_less: int | None = Field(default=None, alias="from")
    not_more: int | None = Field(default=None, alias="to")
    currency: Currency
    gross: bool
    mode: VacancySalaryRangeMode
    frequency: VacancySalaryRangeFrequency | None = None


class VacancyType(BaseModel):
    id: str
    name: str


class VacancyAddress(BaseModel):
    id: str
    city: str
    street: str
    building: str | None = None
    lat: float
    lng: float
    description: str | None = None
    raw: str
    metro: VacancyMetroStation | None = None
    metro_stations: list[VacancyMetroStation] = Field(default_factory=list)


class VacancyBranding(BaseModel):
    type: str
    tariff: str | None = None


class VacancyEmployer(BaseModel):
    id: str
    name: str
    url: str
    alternate_url: str
    logo_urls: EmployerLogoURL | None = None
    vacancies_url: str
    country_id: int
    accredited_it_employer: bool
    trusted: bool


class VacancySnippet(BaseModel):
    requirement: str
    responsibility: str


class VacancyContact(BaseModel):
    name: str
    email: str
    phones: list[PhoneNumber] = Field(default_factory=list)
    call_tracking_enabled: bool | None = None


class VacancySchedule(BaseModel):
    id: str
    name: str


class VacancyWorkingTimeInterval(BaseModel):
    id: str
    name: str


class VacancyWorkFormat(BaseModel):
    id: str
    name: str


class VacancyWorkingHours(BaseModel):
    id: str
    name: str


class VacancyWorkScheduleByDays(BaseModel):
    id: str
    name: str


class VacancyProfessionalRole(BaseModel):
    id: str
    name: str


class VacancyExperience(BaseModel):
    id: str
    name: str


class VacancyEmployment(BaseModel):
    id: str
    name: str


class VacancyEmploymentForm(BaseModel):
    id: str
    name: str


class Vacancy(BaseModel):
    id: str
    premium: bool
    name: str
    department: VacancyDepartment | None = None
    has_test: bool
    response_letter_required: bool
    area: VacancyArea
    salary: VacancySalary | None = None
    salary_range: VacancySalaryRange | None = None
    type: VacancyType
    address: VacancyAddress | None = None
    response_url: str | None = None
    sort_point_distance: float | None = None
    published_at: datetime.datetime
    created_at: datetime.datetime
    archived: bool
    apply_alternate_url: str
    branding: VacancyBranding | None = None
    show_logo_in_search: bool | None = None
    show_contacts: bool
    insider_interview: bool | None = None
    url: str
    alternate_url: str
    relations: list[Any] = Field(default_factory=list)
    employer: VacancyEmployer
    snippet: VacancySnippet
    contacts: VacancyContact | None = None
    schedule: VacancySchedule
    working_days: list[Any] = Field(default_factory=list)
    working_time_intervals: list[VacancyWorkingTimeInterval] = Field(
        default_factory=list
    )
    working_time_modes: list[Any] = Field(default_factory=list)
    accept_temporary: bool
    fly_in_fly_out_duration: list[Any] = Field(default_factory=list)
    work_format: list[VacancyWorkFormat] = Field(default_factory=list)
    working_hours: list[VacancyWorkingHours] = Field(default_factory=list)
    work_schedule_by_days: list[VacancyWorkScheduleByDays] = Field(
        default_factory=list
    )
    night_shifts: bool
    professional_roles: list[VacancyProfessionalRole] = Field(
        default_factory=list
    )
    accept_incomplete_resumes: bool
    experience: VacancyExperience
    employment: VacancyEmployment
    employment_form: VacancyEmploymentForm
    internship: bool
    adv_response_url: str | None = None
    is_adv_vacancy: bool
    adv_context: str | None = None
