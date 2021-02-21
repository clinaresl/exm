# Introduction #

``exm`` is a Python package that automates the scheduling of UC3M exams. To this
end, it provides a script with the same name, `exm`.

`exm` enables the arbitrary combination of both /unit/ and /binary/ date and
time constraints between subjects of the same grade or across different grades.
It also allows the definition of different *setup* times required for the
preparation of any exam. The solutions obtained are not only compliant with
these user-defined constraints but also with current UC3M regulations.

# Requirements #

``exm`` requires the following Python packages:

* [icalendar](https://pypi.org/project/icalendar/) >= 4.0.7
* [pyexcel](https://pypi.org/project/pyexcel/) >= 0.6.6
  and make sure to install the [pyexcel-xlsx](https://pypi.org/project/pyexcel-xlsx/) >= 0.6.0 plugin
* [python-constraint](https://pypi.org/project/python-constraint/) >= 1.4.0
* [pytz](https://pypi.org/project/pytz/) >= 2020.1
* [xlsxwriter](https://pypi.org/project/XlsxWriter/) >= 1.3.7

In addition, `exm` has been developed with Python 3.8 and it requires Python 3.6
at least.


# Installation #

Download the software cloning the git repository with the following command:

    $ git clone https://github.com/clinaresl/exm.git

a directory called `exm` will be automatically created. Go to that directory
and execute the following statements:

    $ cd exm
    $ pip install .


# Usage #

`exm` takes an `.xlsx` spreadsheet as input with information about subjects and
various constraints for scheduling the exams, and produces another `.xlsx`
spreadsheet with a full schedule (i.e., date and time) for each exam. 

The input spreadsheet should contain a sheet named `Timeslots` with the
available date and time slots for making the exams. The following Figure shows
the contents of this sheet in the file `data/example-1.xlsx`:

| Fecha | Slot #1 | Slot #2 | Slot #3 | Slot #4 |
|:-----:|:-------:|:-------:|:-------:|:-------:|
|21/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|22/05/21 | 08:30 AM |12:30 PM | | |
|24/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|25/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|26/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|27/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|28/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|29/05/21 | 08:30 AM | 12:30 PM | | |
|31/05/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|01/06/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|02/06/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|03/06/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |
|04/06/21 | 08:30 AM | 12:30 PM | 03:30 PM | 06:30 PM |

The headers must be named precisely as shown in the previous Table. Note the
date is given in spanish format just because the locale of the input spreadsheet
is defined that way, but other formats are also allowed.

Next, the input spreadsheet must have a sheet for each grade. For the purposes
of ilustration, the following Table shows the contents of the file
`data/example-1.xlsx` for scheduling the exams of the first course of **Applied
Mathematics and Computing** (abbreviated as *GMAC* in spanish):

| Asignatura | Curso | Cuatrimestre |Fecha | Hora |
|:----------:|:-----:|:------------:|:----:|:----:|
|Cálculo diferencial | 1 | 1 |  | |
|Fundamentos de Álgebra | 1 |1 | | |
|Programación | 1 | 1 | | |
| Álgebra Lineal | 1 | 1 | | |
| Técnicas de expresión oral y escrita | 1 | 1 | |
|Habilidades: Humanidades I | 1 | 1 | |
| Cálculo Integral | 1 | 2 | | |
| Cálculo Vectorial | 1 | 2 | | |
| Geometría Lineal | 1 | 2 | | |
| Técnicas de Programación | 1 | 2 | | |
| Matemática Discreta | 1 | 2 | | |

Again, headers must be named precisely as in the Table. Note the presence of
columns `Fecha` (date) and `Hora` (time). These can be used for introducing any
combination of unit and binary constraints for selecting the date and/or the
time of each exam. Given the current contents of this input spreadsheet, the
command:

```Shell
$ exm --master data/example-1.xlsx
```

produces a feasible schedule for all the exams found in `data/example-1.xlsx`.
The input spreadsheet is specified with `--master` and unless another name is
given for the output spreadsheet with the directive `--output`, it is named
after the input file adding `-timetable`. The contents of the output spreadsheet
`data/example-1-timetable.xlsx` are shown next:

| Asignatura | Curso | Cuatrimestre |Fecha | Hora |
|:----------:|:-----:|:------------:|:----:|:----:|
| Habilidades: Humanidades I | 1 | 1 | 2021-05-24 | 12:30:00 |
| Técnicas de expresión oral y escrita | 1 | 1 | 2021-05-25 | 12:30:00 |
| Álgebra Lineal | 1 | 1 | 2021-05-26 | 12:30:00 |
| Programación | 1 | 1 | 2021-05-27 | 12:30:00 |
| Fundamentos de Álgebra | 1 | 1 | 2021-05-28 | 12:30:00 |
| Cálculo diferencial | 1 | 1 | 2021-05-29 | 12:30:00 |
| Matemática Discreta | 1 | 2 | 2021-05-31 | 18:30:00 |
| Técnicas de Programación | 1 | 2 | 2021-06-01 | 18:30:00 |
| Geometría Lineal | 1 | 2 | 2021-06-02 | 18:30:00 |
| Cálculo Vectorial | 1 | 2 | 2021-06-03 | 18:30:00 |
| Cálculo Integral | 1 | 2 | 2021-06-04 | 18:30:00 |

In the absence of other constraints in the input spreadsheet the only one that
applies is that according to the UC3M regulations, two consecutive exams of the
same course should leave a space of at least 24 hours in between. The produced
schedule is actually compliant with this constraint. For improving analysis of
the resulting schedule, the output spreadsheet has /autofilters/ for all columns
but the first one.

Additionally, it is possible to use `--ical` to specify the name of an icalendar
file which can then be exported to any utility. The following Figure shows a
partial view of the result of importing the preceding schedule into Google
Calendar:

![Google Calendar example-1](https://github.com/clinaresl/exm/blob/main/figs/example-1.png)

As it can be seen, the exams last by default one hour. This is not relevant
indeed, as the time slots given in the input spreadsheet should be wide enough
to allocate exams of any duration.

Of course, the input spreadsheet might contain various sheets for scheduling the
exams of different grades but maybe not all have to be scheduled. `exm` provides
a selection criteria mechanism based on the combination of three flags, namely
`--grade`, `--course` and `--semester`. In case they are used only one argument
can be given, and only records simultaneously satisfying all parameters are
originally accepted. Recaping:

```Shell
$ exm --master data/example-1.xlsx --grade GMAC --semester 2 --output schedule-GMAC --ical GMAC
```

will schedule only the exams of the first semester of those subjects shown in
the sheet `GMAC` (in spite of others being present in the input spreadsheet).
The result will be recorded in the spreadsheet `schedule-GMAC.xlsx`, and also an
iCalendar will be generated and written to `GMAC.ics`. Note that it is not
required to provide the extensions of output filenames as they are automatically
completed.

## Constraints ##

`exm` provides simple means for specifying any combination of *unit* and
*binary* constraints affecting the selection of the date and/or the time of an
exam.

These contraints have to be given in the columns `Fecha` and `Hora` of the input
spreadsheet. An arbitrary number of them can be given in a comma-separated list
of constraints ---see examples below.

### Unit constraints ###

A unit constraint binds the value of a field (either the date or time of an
exam) to a constant value (either a date or a time) with the usage of an
operator. The available operators are: `=`, `!=`, `<`, `<=`, `>` and `>=` with a
self-explanatory meaning. For example: `= 28/05/2021` actually fixes the date of
one subject (also known as *records*), whereas `!= 28/05/2021` just forbids one
specific date; `< 18:30` serves to pick up any time before 6:30 PM, whereas `>=
18:30` necessarily fixes the time of an exam given the timeslots defined in the
previous example.

To avoid misleading behaviours while operating with the input spreadsheet, the
operator `=` can be always skipped, e.g., `8:30` is interpreted as `= 8:30`. In
case there is a reason to explicitly use it, it is advised to leave a heading
blank space, or the spreadsheet might confuse the unit constraint with a
*formula*.

<a name="binary-constraints"/>
### Binary constraints ###

Binary constraints are much alike unit constraints. The same operators are
available for defining them and `=` is also assumed by default. The difference
is that instead of providing a constant date or time, they accept a reference to
another record.

Records are identified by the cell where the name of a subject is given, i.e.,
in the column `Asignatura`. Thus, if one subject (say *Cálculo diferencial*) is
given the binary constraint `> B13` in the date column, then any feasible
solution should allocate this exam a date after the exam selected for the record
shown in cell B13, say *Técnicas de Programación*. Likewise, if `!= B10` is
given in the time column of one entry, then the time chosen for that specific
exam must be different than the time selected for the subject shown in cell B10.

### Combination of constraints ###

Either unit or binary constraints can be arbitrarily combined as a
comma-separated list. 

The following table shows the contents of the sheet `GMAC` in the spreadsheet
`data/example-2.xlsx`:

| Asignatura | Curso | Cuatrimestre |Fecha | Hora |
|:----------:|:-----:|:------------:|:----:|:----:|
|Cálculo diferencial | 1 | 1 | > B13, <B5 | |
|Fundamentos de Álgebra | 1 |1 | | 15:30 |
|Programación | 1 | 1 | | |
| Álgebra Lineal | 1 | 1 | | != B10 |
| Técnicas de expresión oral y escrita | 1 | 1 | |
|Habilidades: Humanidades I | 1 | 1 | |
| Cálculo Integral | 1 | 2 | < B4, >= 2021/05/22 | |
| Cálculo Vectorial | 1 | 2 | | <= B12 |
| Geometría Lineal | 1 | 2 | | > B5 |
| Técnicas de Programación | 1 | 2 | | |
| Matemática Discreta | 1 | 2 | | |

The contents of the sheet `Timeslots` of this input spreadsheet are identical to
those shown in the first example. Therefore, the following is a correct schedule
which actually satisfies all constraints shown in the preceding Table:

| Asignatura | Curso | Cuatrimestre |Fecha | Hora |
|:----------:|:-----:|:------------:|:----:|:----:|
| Habilidades: Humanidades I | 1 | 1 | 2021-05-22 | 12:30:00 |
| Técnicas de expresión oral y escrita | 1 | 1 | 2021-05-24 | 12:30:00 |
| Programación | 1 | 1 | 2021-05-25 | 12:30:00 |
| Álgebra Lineal | 1 | 1 | 2021-05-29 | 12:30:00 |
| Cálculo diferencial | 1 | 1 | 2021-06-03 | 15:30:00 |
| Fundamentos de Álgebra | 1 | 1 | 2021-06-04 | 15:30:00 |
| Matemática Discreta | 1 | 2 | 2021-05-26 | 12:30:00 |
| Técnicas de Programación | 1 | 2 | 2021-05-27 | 12:30:00 |
| Cálculo Vectorial | 1 | 2 | 2021-05-28 | 12:30:00 |
| Cálculo Integral | 1 | 2 | 2021-05-31 | 18:30:00 |
| Geometría Lineal | 1 | 2 | 2021-06-01 | 18:30:00 |

## Scheduling across grades ##

The [School of Engineering of UC3M](https://www.uc3m.es/soe/home) provides a
wide range of Bachelor Degrees. Some are double grades (such as the [Dual
Bachelor in Computer Science and Engineering and Business
Administration](https://www.uc3m.es/bachelor-degree/computer-science-business),
abbreviated as *GII-ADE* in spanish) and others, even if they are not double
degrees, also share some lectures with other degrees, such as the [Bachelor in
Applied Mathematics and
Computing](https://www.uc3m.es/bachelor-degree/applied-mathematics-computing)
(abbreviated as *GMAC* in spanish) and the [Bachelor in Computer Science and
Engineering](https://www.uc3m.es/bachelor-degree/computer-science)
---abbreviated as *GII* in spanish. As an example, the subject *Heuristics and
Optimization* was originally lectured in GII, but nowadays there also enrolled
students from both GII-ADE and GMAC.

Thus, to schedule the exam of a specific subject, it is not only necessary to
take into account the constraints of the grade the subject belongs to, but also
the constraints involved in the scheduling of the same subject with those of
other grades. This means that, in our running example, the exam of *Heuristics
and Optimization* must be scheduled on a date and time that is compatible, not
only with other exams of GII, but also with the exams of GMAC and GII-ADE.

With this purpose in mind, `exm` allows referencing any record in any sheet (or,
alternatively in any grade) when setting up a [binary
constraint](https://github.com/clinaresl/exm/binary-constraint).

# License #

exm is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

exm is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with exm.  If not, see <http://www.gnu.org/licenses/>.


# Author #

Carlos Linares Lopez <carlos.linares@uc3m.es>
