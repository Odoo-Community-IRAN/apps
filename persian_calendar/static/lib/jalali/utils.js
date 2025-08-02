function JDate(input) {
    this.locale = 'fa';
    this.date = new Date();
    this.setup(input);
}

JDate.Utils = {
    e2p: s => s.replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]),
    p2e: s => s.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)),
    faWeekDays: ['یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'],
    faWeekDaysShort: ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش'],
    faMonths: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',],
    BREAKS: [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178],
    toJalali: function (arg1, arg2 = undefined, arg3 = undefined) {
        const gregorian = arg1 instanceof Date ? arg1 : null;
        const year = gregorian ? gregorian.getFullYear() : arg1;
        const month = gregorian ? gregorian.getMonth() + 1 : arg2;
        const date = gregorian ? gregorian.getDate() : arg3;
        const julian = this.gregorianToJulian(year, month, date);

        return this.julianToJalali(julian);
    },
    toGregorian: function (year, month, date) {
        const julian = this.jalaliToJulian(year, month, date);
        return this.julianToGregorian(julian);
    },
    isValid: function (year, month, date, hours = 0, minutes = 0, seconds = 0, ms = 0) {
        return year >= -61 && year <= 3177 && month >= 1 && month <= 12 && date >= 1 && date <= this.monthLength(year, month) && hours >= 0 && hours <= 23 && minutes >= 0 || minutes <= 59 && seconds >= 0 || seconds <= 59 && ms >= 0 || ms <= 999;
    },
    isLeapYear: function (year) {
        return this.calculateLeap(year) === 0;
    },
    monthLength: function (year, month) {
        if (month <= 6) return 31;
        if (month <= 11) return 30;
        if (this.isLeapYear(year)) return 30;
        return 29;
    },
    calculateLeap: function (year, calculated) {
        const bl = this.BREAKS.length;
        let jp = calculated ? calculated.jp : this.BREAKS[0];
        let jump = calculated ? calculated.jump : 0;

        if (!calculated) {
            if (year < jp || year >= this.BREAKS[bl - 1]) {
                throw new Error(`Invalid Jalali year ${year}`);
            }

            for (let i = 1; i < bl; i++) {
                const jm = this.BREAKS[i];
                jump = jm - jp;
                if (year < jm) break;
                jp = jm;
            }
        }

        let n = year - jp;
        if (jump - n < 6) {
            n = n - jump + this.div(jump + 4, 33) * 33;
        }
        let leap = this.mod(JDate.Utils.mod(n + 1, 33) - 1, 4);
        if (leap === -1) {
            leap = 4;
        }

        return leap;
    },
    calculateJalali: function (year, calculateLeap = true) {
        const bl = this.BREAKS.length;
        const gregorianYear = year + 621;
        let leapJ = -14;
        let jp = this.BREAKS[0];

        if (year < jp || year >= this.BREAKS[bl - 1]) {
            throw new Error(`Invalid Jalali year ${year}`);
        }

        let jump = 0;
        for (let i = 1; i < bl; i++) {
            const jm = this.BREAKS[i];
            jump = jm - jp;
            if (year < jm) break;
            leapJ = leapJ + this.div(jump, 33) * 8 + this.div(this.mod(jump, 33), 4);
            jp = jm;
        }

        let n = year - jp;
        leapJ = leapJ + this.div(n, 33) * 8 + this.div(this.mod(n, 33) + 3, 4);
        if (this.mod(jump, 33) === 4 && (jump - n) === 4) {
            leapJ += 1;
        }

        const leapG = this.div(gregorianYear, 4) - this.div((this.div(gregorianYear, 100) + 1) * 3, 4) - 150;
        const march = 20 + leapJ - leapG;

        return {
            gregorianYear, march, leap: calculateLeap ? this.calculateLeap(year, { jp, jump }) : -1
        };
    },
    jalaliToJulian: function (year, month, date) {
        const r = this.calculateJalali(year, false);

        return this.gregorianToJulian(r.gregorianYear, 3, r.march) + (month - 1) * 31 - this.div(month, 7) * (month - 7) + date - 1;
    },
    julianToJalali: function (julian) {
        const gregorian = this.julianToGregorian(julian);
        let year = gregorian.year - 621;

        const r = this.calculateJalali(year);
        const julian1F = this.gregorianToJulian(gregorian.year, 3, r.march);

        let k = julian - julian1F;
        if (k >= 0) {
            if (k <= 185) {
                return {
                    year, month: 1 + this.div(k, 31), date: this.mod(k, 31) + 1
                };
            } else {
                k -= 186;
            }
        } else {
            year -= 1;
            k += 179;
            if (r.leap === 1) k += 1;
        }

        return {
            year, month: 7 + this.div(k, 30), date: this.mod(k, 30) + 1
        };
    },
    gregorianToJulian: function (year, month, date) {
        const julian = this.div((year + this.div(month - 8, 6) + 100100) * 1461, 4) + this.div(153 * this.mod(month + 9, 12) + 2, 5) + date - 34840408;

        return (julian - this.div(this.div(year + 100100 + this.div(month - 8, 6), 100) * 3, 4) + 752);
    },
    julianToGregorian: function (julian) {
        let j = 4 * julian + 139361631;
        j = j + this.div(this.div(4 * julian + 183187720, 146097) * 3, 4) * 4 - 3908;

        const i = this.div(this.mod(j, 1461), 4) * 5 + 308;

        const date = this.div(this.mod(i, 153), 5) + 1;
        const month = this.mod(this.div(i, 153), 12) + 1;
        const year = this.div(j, 1461) - 100100 + this.div(8 - month, 6);

        return { year, month, date };
    },
    jalaliWeek: function ({ year, month, date }) {
        const dayOfWeek = this.toDate(year, month, date).getDay();
        const startDayDifference = dayOfWeek === 6 ? 0 : -(dayOfWeek + 1);
        const endDayDifference = 6 + startDayDifference;

        return {
            saturday: this.julianToJalali(this.jalaliToJulian(year, month, date + startDayDifference)),
            friday: this.julianToJalali(this.jalaliToJulian(year, month, date + endDayDifference))
        };
    },
    toDate: function (year, month, date, hours = 0, minutes = 0, seconds = 0, ms = 0) {
        const gregorian = this.toGregorian(year, month, date);

        return new Date(gregorian.year, gregorian.month - 1, gregorian.date, hours, minutes, seconds, ms);
    },
    div: function (a, b) {
        return ~~(a / b);
    },
    mod: function (a, b) {
        return a - ~~(a / b) * b;
    },
};
JDate.Helper = {
    toJalali: function (date) {
        const jalali = JDate.Utils.toJalali(date);
        jalali.month -= 1;
        return jalali;
    },

    toGregorian: function (year, month, date) {
        const gregorian = JDate.Utils.toGregorian(year, month + 1, date);
        gregorian.month -= 1;
        return gregorian;
    }, monthLength: function (year, month) {
        month = JDate.Utils.mod(month, 12);
        year += JDate.Utils.div(month, 12);
        if (month < 0) {
            month += 12;
            year -= 1;
        }
        return JDate.Utils.monthLength(year, month + 1);
    }, normalizeHours: function (date, hours) {
        let meridian = null;
        if (String(date).toLowerCase().includes('am')) meridian = 'am';
        if (String(date).toLowerCase().includes('pm')) meridian = 'pm';

        if (meridian === 'am' && hours === 12) return 0;
        if (meridian === 'pm' && (hours >= 1 && hours <= 11)) return hours + 12;

        return (meridian !== null && hours > 12) ? -1 : hours;
    }, normalizeMilliseconds: function (ms) {
        if (ms.length === 1) return Number(ms) * 100; else if (ms.length === 2) return Number(ms) * 10;
        return ms.length > 3 ? -1 : Number(ms);
    }, zeroPad: function (value, maxLength = 2) {
        return String(value).padStart(maxLength, '0');
    }, throwError: function (value) {
        throw new Error(`Invalid: ${value}`);
    }
};
JDate.prototype.setup = function (input) {
    if (input) {
        // jalali format string
        if (typeof input === 'string') {
            this.date = this.parse(input);
        } else if (input instanceof luxon.DateTime) {
            this.date = input.toJSDate();
        } else if (input instanceof Date) {
            this.date = input;
        }
    }
    this.updateJObject();
};
JDate.prototype.parse = function (stringValue) {
    const value = JDate.Utils.p2e(stringValue);
    const matches = (value.match(/\d\d?\d?\d?/g) || []);
    const empty = new Array(7).fill('0');
    const [year, month, date, hours, minutes, seconds, ms] = [...matches, ...empty]
        .slice(0, 7)
        .map((val, index) => {
            let numberValue = Number(val);
            if (index === 3) numberValue = JDate.Helper.normalizeHours(value, Number(val)); else if (index === 6) numberValue = JDate.Helper.normalizeMilliseconds(val);
            return numberValue;
        });

    if (!JDate.Utils.isValid(year, month, date, hours, minutes, seconds, ms)) {
        JDate.Utils.throwError(stringValue);
    }

    return JDate.Utils.toDate(year, month, date, hours, minutes, seconds, ms);
};
JDate.prototype.updateJObject = function updateJObject() {
    this.jObject = JDate.Utils.toJalali(this.date);
    return this;
};
JDate.prototype.timestamp = function timestamp(value) {
    return new JDate(new Date(value));
};
JDate.prototype.clone = function clone() {
    return this.timestamp(+this);
};
JDate.prototype.add = function (unit, value, inplace = false) {
    const clone = inplace ? this : this.clone();
    switch (unit) {
        case 'year':
        case 'years':
            clone.setFullYear(this.getFullYear() + value);
            break;
        case 'month':
        case 'months':
            clone.setMonth(this.getMonth() + value);
            break;
        case 'week':
        case 'weeks':
            clone.date.setDate(this.date.getDate() + (value * 7));
            break;
        case 'day':
        case 'days':
            clone.date.setDate(this.date.getDate() + value);
            break;
        case 'hour':
        case 'hours':
            clone.date.setHours(this.date.getHours() + value);
            break;
        case 'minute':
        case 'minutes':
            clone.date.setMinutes(this.date.getMinutes() + value);
            break;
        case 'second':
        case 'seconds':
            clone.date.setSeconds(this.date.getSeconds() + value);
            break;
        case 'millisecond':
        case 'milliseconds':
            clone.date.setMilliseconds(this.date.getMilliseconds() + value);
            break;
    }
    return clone.updateJObject();
};
JDate.prototype.subtract = function (unit, value, inplace = false) {
    return this.add(unit, value * -1, inplace);
};
JDate.prototype.toLocale = function toLocale(locale) {
    this.locale = locale;
    return this;
};
JDate.prototype.getJSDate = function getJSDate() {
    return this.date;
};
JDate.prototype.getLDate = function getLDate() {
    return luxon.DateTime.fromJSDate(this.date);
};
JDate.prototype.gregorian = function gregorian(stringValue) {
    const value = JDate.Utils.p2e(stringValue);
    const date = new Date(value);
    if (Number.isNaN(+date)) JDate.Helper.throwError(stringValue);
    return new JDate(date);
};
JDate.prototype.valueOf = function valueOf() {
    return +this.date;
};
JDate.prototype.getFullYear = function getFullYear() {
    return JDate.Helper.toJalali(this.date).year;
};
JDate.prototype.getMonth = function getMonth() {
    return JDate.Helper.toJalali(this.date).month;
};
JDate.prototype.getDate = function () {
    return JDate.Helper.toJalali(this.date).date;
};
JDate.prototype.getHours = function () {
    return this.date.getHours();
};
JDate.prototype.getMinutes = function () {
    return this.date.getMinutes();
};
JDate.prototype.getSeconds = function () {
    return this.date.getSeconds();
};
JDate.prototype.getMilliseconds = function () {
    return this.date.getMilliseconds();
};
JDate.prototype.update = function (value) {
    this.date = new Date(value.year, value.month, value.date, this.getHours(), this.getMinutes(), this.getSeconds(), this.getMilliseconds());
    this.updateJObject();
};
JDate.prototype.setFullYear = function (value) {
    const jalaliDate = JDate.Helper.toJalali(this.date);
    const date = Math.min(jalaliDate.date, JDate.Utils.monthLength(value, jalaliDate.month));
    const gregorianDate = JDate.Helper.toGregorian(value, jalaliDate.month, date);
    this.update(gregorianDate);
    return this;
};
JDate.prototype.setMonth = function (value) {
    const jalaliDate = JDate.Helper.toJalali(this.date);
    const date = Math.min(jalaliDate.date, JDate.Utils.monthLength(jalaliDate.year, value));
    this.setFullYear(jalaliDate.year + JDate.Utils.div(value, 12));
    value = JDate.Utils.mod(value, 12);
    if (value < 0) {
        value += 12;
        this.add('year', -1, true);
    }
    const gregorianDate = JDate.Helper.toGregorian(this.getFullYear(), value, date);
    this.update(gregorianDate);
    return this;
};
JDate.prototype.setDate = function (value) {
    const jalaliDate = JDate.Helper.toJalali(this.date);
    const gregorianDate = JDate.Helper.toGregorian(jalaliDate.year, jalaliDate.month, value);
    this.update(gregorianDate);
    return this;
};
JDate.prototype.setHours = function (value) {
    this.date.setHours(value);
    return this;
};
JDate.prototype.setMinutes = function (value) {
    this.date.setMinutes(value);
    return this;
};
JDate.prototype.setSeconds = function (value) {
    this.date.setSeconds(value);
    return this;
};
JDate.prototype.setMilliseconds = function (value) {
    this.date.setMilliseconds(value);
    return this;
};
JDate.prototype.isLeapYear = function () {
    return JDate.Utils.isLeapYear(JDate.Helper.toJalali(this.date).year);
};
JDate.prototype.monthLength = function () {
    const jalaliDate = JDate.Helper.toJalali(this.date);
    return JDate.Utils.monthLength(jalaliDate.year, jalaliDate.month);
};
JDate.prototype.startOf = function (unit) {
    const clone = this.clone();
    if (unit === 'year') {
        clone.setMonth(0);
    }
    if (unit === 'year' || unit === 'month') {
        clone.setDate(1);
    }
    if (unit === 'week') {
        const dayOfDate = this.date.getDay();
        const startOfWeek = this.date.getDate() - (dayOfDate === 6 ? 0 : this.date.getDay() + 1);
        clone.date.setDate(startOfWeek);
    }
    if (['year', 'month', 'week', 'day'].includes(unit)) {
        clone.setHours(0);
    }
    return clone.setMinutes(0).setSeconds(0).setMilliseconds(0).updateJObject();
};
JDate.prototype.endOf = function (unit) {
    return this.startOf(unit).add(unit, 1).setMilliseconds(-1).updateJObject();
};
JDate.prototype.format = function (format = 'YYYY/MM/DD HH:mm:ss', gregorian = false) {
    let value = String(format);
    const ref = gregorian ? this.date : this;

    const monthIndex = ref.getMonth();
    const dayIndex = this.date.getDay();

    const year = ref.getFullYear();
    const month = monthIndex + 1;
    const date = ref.getDate();

    let hours = ref.getHours();
    const minutes = ref.getMinutes();
    const seconds = ref.getSeconds();
    const ms = ref.getMilliseconds();

    if (!gregorian) {
        if (format.includes('dddd')) value = value.replace('dddd', JDate.Utils.faWeekDays[dayIndex]);
        if (format.includes('dd')) value = value.replace('dd', JDate.Utils.faWeekDaysShort[dayIndex]);
        if (format.includes('MMMM')) value = value.replace('MMMM', JDate.Utils.faMonths[monthIndex]);
    }

    if (format.includes('YYYY')) value = value.replace('YYYY', String(year));
    if (format.includes('MM')) value = value.replace('MM', JDate.Helper.zeroPad(month));
    if (format.includes('DD')) value = value.replace('DD', JDate.Helper.zeroPad(date));

    if (format.includes('HH')) value = value.replace('HH', JDate.Helper.zeroPad(hours));
    if (format.includes('mm')) value = value.replace('mm', JDate.Helper.zeroPad(minutes));
    if (format.includes('ss')) value = value.replace('ss', JDate.Helper.zeroPad(seconds));
    if (format.includes('SSS')) value = value.replace('SSS', JDate.Helper.zeroPad(ms, 3));
    if (format.includes('hh')) {
        const symbol = hours >= 12 ? 'pm' : 'am';
        if (format.includes('a')) value = value.replace('a', symbol);
        if (format.includes('A')) value = value.replace('A', symbol.toUpperCase());
        if (hours === 0) hours = 12;
        if (hours >= 13 && hours <= 23) hours -= 12;
        value = value.replace('hh', JDate.Helper.zeroPad(hours));
    }
    return this.locale === 'fa' ? JDate.Utils.e2p(value) : value;
};
JDate.prototype.gregorian = function (format = 'YYYY-MM-DD HH:mm:ss') {
    return this.format(format, true);
};

JDate.prototype.getWeekNumber = function () { // in year
    let jYearStart = this.clone().startOf('year')
    jYearStart = jYearStart.add('days', 6 - jYearStart.getLDate().weekday).getLDate();
    const diffDays = this.getLDate().diff(jYearStart, 'day').days;
    return Math.trunc(diffDays / 7) + 1;
};