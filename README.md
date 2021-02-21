# Introduction #

``exm`` is a Python package that automates the scheduling of UC3M exams. To this
end, it provides a script with the same name, `exm`.


# Requirements #

``exm`` requires the following Python packages:

* [icalendar](https://pypi.org/project/icalendar/) >= 4.0.7
* [pyexcel](https://pypi.org/project/pyexcel/) >= 0.6.6
  and make sure to install the [pyexcel-xlsx](https://pypi.org/project/pyexcel-xlsx/) >= 0.6.0 plugin
* [python-constraint](https://pypi.org/project/python-constraint/) >= 1.4.0
* [pytz](https://pypi.org/project/pytz/) >= 2020.1
* [xlsxwriter](https://pypi.org/project/XlsxWriter/) >= 1.3.7


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

Note the date is given in spanish format just because the locale of the input
spreadsheet is defined that way, but other formats are also allowed. The headers
must be named precisely as shown in the previous Table. 

Next, the input spreadsheet must have a sheet for each grade. For the purposes
of ilustration, the following Table shows the contents of the file
`data/example-1.xlsx` for scheduling the exams of the first course of **Applied
Mathematics and Computing** (abbreviated as *GMAC* in spanish):

| Asignatura | Curso | Cuatrimestre |Fecha | Hora |
|:----------:|:-----:|:------------:|:----:|:----:|
|Cálculo diferencial | 1 | 1 |  | |
|Fundamentos de Álgebra | 1 |1 | | |
|Programación | 1 | 1 | $GII.B6 | $GII.B6 |
| Álgebra Lineal | 1 | 1 | $GII.B7 | $GII.B7 |
| Técnicas de expresión oral y escrita | 1 | 1 | |
|Habilidades: Humanidades I | 1 | 1 | |
| Cálculo Integral | 1 | 2 | | |
| Cálculo Vectorial | 1 | 2 | | |
| Geometría Lineal | 1 | 2 | | |
| Técnicas de Programación | 1 | 2 | | |
| Matemática Discreta | 1 | 2 | $GII.B14 | $GII.B14 |


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
