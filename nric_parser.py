# Copyright 2011 sweemeng<sweester@gmail.com. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY SWEEMENG ''AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of sweemeng.

import re
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import datetime
from scraper.nrd_local import NRDLocal
from scraper.nrd_oversea import NRDOversea
import json


class ICParser:
    def __init__(self,ic,state_file='data/state_code.json',country_file='data/country_code.json'):
        self.state_file = state_file
        self.country_file = country_file
        ic_with_dash = r'\d{6}-\d{2}-\d{4}'
        ic_digits_only = r'\d{12}'
        ic_split_pattern = r'(\d{6})(\d{2})(\d{4})'
        if re.match(ic_digits_only,ic):
            self.ic_token = re.split(ic_split_pattern,ic)
            self.ic_token = [i for i in self.ic_token if i]
        elif re.match(ic_with_dash,ic):
            self.ic_token = ic.split('-')
        else:
            raise InvalidFormatException(ic)

        self.set_gender()
        self.set_birth_date()
        self.set_birth_place()

    def set_birth_date(self):
        year = int(self.ic_token[0][:2])
        today_year = int(str(datetime.date.today().year)[2:])

        # if ic year more than current year, 
        # add 19 (assuming age can max to 100 years old), 
        # else add 20
        if year > today_year:
            self.birth_date = parse('19'+self.ic_token[0]).date()
        else:
            self.birth_date = parse('20'+self.ic_token[0]).date()

        if self.birth_date > datetime.date.today():
            raise DateInFutureException(self.birth_date)

        today = datetime.date.today()
        date_diff = relativedelta(today,self.birth_date)
        
        if date_diff.years < 12:
            raise InvalidDateException(self.birth_date)

    def set_gender(self):
        last_no = self.ic_token[2][-1]
        if int(last_no) % 2:
            self.gender = 'M'
        else:
            self.gender = 'F'
    
    def set_birth_place(self):
        if self.state_file:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
        else:
            local = NRDLocal()
            data = local.data

        self.birth_place = ''

        try:
            self.birth_place = data[self.ic_token[1]]
            return
        except KeyError:
            pass            

        if self.country_file:
            with open(self.country_file, 'r') as f:
                data = json.load(f)
        else:
            oversea = NRDOversea()
            data = oversea.data

        try: 
            self.birth_place = ','.join(data[self.ic_token[1]])
        except KeyError:
            raise InvalidBirthPlace(self.ic_token[1])


class InvalidFormatException(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


class InvalidDateException(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


class InvalidBirthPlace(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


class DateInFutureException(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
