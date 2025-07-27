/** @odoo-module **/

import { isInRange, today } from '@web/core/l10n/dates';
import { localization } from '@web/core/l10n/localization';
import { patch } from '@web/core/utils/patch';
import { DateTimePicker } from '@web/core/datetime/datetime_picker';
import { _t } from '@web/core/l10n/translation';

const { DateTime, Info } = luxon;

/**
 * @param {DateTime} date
 */
const getStartOfDecade = (date) => Math.floor(date.year / 10) * 10;

/**
 * @param {DateTime} date
 */
const getStartOfCentury = (date) => Math.floor(date.year / 100) * 100;

/**
 * @param {DateTime} date
 */
const getStartOfWeek = (date) => {
    const { weekStart } = localization;
    return date.set({ weekday: date.weekday < weekStart ? weekStart - 7 : weekStart });
};

/**
 * @param {number} min
 * @param {number} max
 */
const numberRange = (min, max) => [...Array(max - min)].map((_, i) => i + min);

/**
 * @param {string} label
 * @returns {string}
 */
const getFormatByLabel = (label) => {
    switch (label) {
        case 'day':
            return 'DD';
        case 'monthShort':
            return 'MMMM';
        case 'year':
            return 'YYYY';
        default:
            return '';
    }
};

/**
 * @param {NullableDateTime | 'today'} value
 * @param {NullableDateTime | 'today'} defaultValue
 */

/**
 * @param {Object} params
 * @param {boolean} [params.isOutOfRange=false]
 * @param {boolean} [params.isValid=true]
 * @param {keyof DateTime} params.label
 * @param {string} [params.extraClass]
 * @param {[DateTime, DateTime]} params.range
 * @returns {DateItem}
 */
const toDateItem = ({ isOutOfRange = false, isValid = true, label, range, extraClass }) => {
    // We just need to set the label as Jalaali to be shown on the DateTimePicker
    const jDate = new JDate(range[0].toJSDate());
    return {
        id: range[0].toISODate(),
        includesToday: isInRange(today(), range),
        isOutOfRange,
        isValid,
        label: localization.code === 'fa_IR' ? jDate.toLocale('fa').format(getFormatByLabel(label)) : String(range[0][label]),
        range,
        extraClass,
    };
};

/**
 * @param {DateItem[]} weekDayItems
 * @returns {WeekItem}
 */
const toWeekItem = (weekDayItems) => ({
    number: new JDate(weekDayItems[3].range[0]).getWeekNumber(),
    days: weekDayItems,
});

// Other constants
const GRID_COUNT = 10;
const GRID_MARGIN = 1;

/**
 * Precision levels
 * @type {Map<PrecisionLevel, PrecisionInfo>}
 */
const PRECISION_LEVELS = new Map()
    .set('days', {
        mainTitle: _t('Select month'),
        nextTitle: _t('Next month'),
        prevTitle: _t('Previous month'),
        step: { month: 1 },
        getTitle: (date, { additionalMonth }) => {
            const jDate = new JDate(date.toJSDate()).toLocale('fa');
            const titles = [`${jDate.format('MMMM')} ${jDate.format('YYYY')}`];
            if (additionalMonth) {
                const next = jDate.add('month', 1).toLocale('fa');
                titles.push(`${next.format('MMMM')} ${next.format('YYYY')}`);
            }
            return titles;
        },
        getItems: (
            date,
            { additionalMonth, maxDate, minDate, showWeekNumbers, isDateValid, dayCellClass }
        ) => {
            date = new JDate(date.toJSDate());
            const startDates = [date];
            if (additionalMonth) {
                startDates.push(date.add('month', 1));
            }
            return startDates.map((date, i) => {
                const jalaliDateStart = date.startOf('month');
                const jalaliDateEnd = date.endOf('month');
                const monthRange = [jalaliDateStart.getLDate(), jalaliDateEnd.getLDate()];

                /** @type {WeekItem[]} */
                const weeks = [];

                // Generate 6 weeks for current month
                let startOfNextWeek = getStartOfWeek(monthRange[0]);
                for (let w = 0; w < 6; w++) {
                    const weekDayItems = [];
                    // Generate all days of the week
                    for (let d = 0; d < 7; d++) {
                        const day = startOfNextWeek.plus({ day: d });
                        const range = [day, day.endOf('day')];
                        const dayItem = toDateItem({
                            isOutOfRange: !isInRange(day, monthRange),
                            isValid: isInRange(range, [minDate, maxDate]) && isDateValid?.(day),
                            label: 'day',
                            range,
                            extraClass: dayCellClass?.(day) || '',
                        });
                        weekDayItems.push(dayItem);
                        if (d === 6) {
                            startOfNextWeek = day.plus({ day: 1 });
                        }
                    }
                    weeks.push(toWeekItem(weekDayItems));
                }

                // Generate days of week labels
                const daysOfWeek = weeks[0].days.map((d) => [
                    d.range[0].weekdayShort,
                    d.range[0].weekdayLong,
                    Info.weekdays('narrow', { locale: d.range[0].locale })[d.range[0].weekday - 1],
                ]);
                if (showWeekNumbers) {
                    daysOfWeek.unshift(['#', _t('Week numbers'), '#']);
                }

                return {
                    id: `__month__${i}`,
                    number: monthRange[0].month,
                    daysOfWeek,
                    weeks,
                };
            });
        },
    })
    .set('months', {
        mainTitle: _t('Select year'),
        nextTitle: _t('Next year'),
        prevTitle: _t('Previous year'),
        step: { year: 1 },
        getTitle: (date) => new JDate(date.toJSDate()).toLocale('fa').format('YYYY'),
        getItems: (date, { maxDate, minDate }) => {
            const jStartOfYear = new JDate(date.toJSDate()).startOf('year');
            return numberRange(0, 12).map((i) => {
                const jStartOfMonth = jStartOfYear.add('month', i);
                const jEndOfMonth = jStartOfMonth.endOf('month');
                const range = [jStartOfMonth.getLDate(), jEndOfMonth.getLDate()];
                return toDateItem({
                    isValid: isInRange(range, [minDate, maxDate]),
                    label: 'monthShort',
                    range,
                });
            });
        },
    })
    .set('years', {
        mainTitle: _t('Select decade'),
        nextTitle: _t('Next decade'),
        prevTitle: _t('Previous decade'),
        step: { year: 10 },
        getTitle: (date) => {
            const jDate = new JDate(date.toJSDate());
            const start = JDate.Utils.e2p(String(getStartOfDecade({ year: jDate.getFullYear() }) - 1));
            const end = JDate.Utils.e2p(String(getStartOfDecade({ year: jDate.getFullYear() }) + 10));
            return `${ start } - ${ end }`;
        },
        getItems: (date, { maxDate, minDate }) => {
            const jDate = new JDate(date.toJSDate());
            const decadeStart = getStartOfDecade({ year: jDate.getFullYear() });
            const startOfDecade = jDate.startOf('year').setFullYear(decadeStart);

            // const startOfDecade = date.startOf('year').set({year: getStartOfDecade(date)});
            return numberRange(-GRID_MARGIN, GRID_COUNT + GRID_MARGIN).map((i) => {
                const jStartOfYear = startOfDecade.add('year', i);
                const endOfYear = jStartOfYear.endOf('year');
                const range = [jStartOfYear.getLDate(), endOfYear.getLDate()];

                return toDateItem({
                    isOutOfRange: i < 0 || i >= GRID_COUNT,
                    isValid: isInRange(range, [minDate, maxDate]),
                    label: 'year',
                    range,
                });
            });
        },
    })
    .set('decades', {
        mainTitle: _t('Select century'),
        nextTitle: _t('Next century'),
        prevTitle: _t('Previous century'),
        step: { year: 100 },
        getTitle: (date) => {
            const jDate = new JDate(date.toJSDate());
            `${getStartOfCentury({ year: jDate.getFullYear() }) - 10} - ${getStartOfCentury({ year: jDate.getFullYear() }) + 100}`;
        },
        getItems: (date, { maxDate, minDate }) => {
            const jDate = new JDate(date.toJSDate());
            const centuryStart = getStartOfCentury({ year: jDate.getFullYear() });
            const startOfCentury = jDate.startOf('year').setFullYear(centuryStart);

            return numberRange(-GRID_MARGIN, GRID_COUNT + GRID_MARGIN).map((i) => {
                const jStartOfDecade = startOfCentury.add('year', i * 10);
                const endOfDecade = jStartOfDecade.add('year', 9).endOf('year');
                const range = [jStartOfDecade.getLDate(), endOfDecade.getLDate()];

                return toDateItem({
                    label: 'year',
                    isOutOfRange: i < 0 || i >= GRID_COUNT,
                    isValid: isInRange(range, [minDate, maxDate]),
                    range,
                });
            });
        },
    });

patch(DateTimePicker.prototype, {
    get activePrecisionLevel() {
        if (localization.code === 'fa_IR') {
            return PRECISION_LEVELS.get(this.state.precision);
        }
        return super.activePrecisionLevel;
    },

    adjustFocus(values, focusedDateIndex) {
        if (localization.code !== 'fa_IR') {
            return super.adjustFocus(values, focusedDateIndex);
        }
        if (
            !this.shouldAdjustFocusDate &&
            this.state.focusDate &&
            focusedDateIndex === this.props.focusedDateIndex
        ) {
            return;
        }

        let dateToFocus =
            values[focusedDateIndex] || values[focusedDateIndex === 1 ? 0 : 1] || today();

        if (
            this.additionalMonth &&
            focusedDateIndex === 1 &&
            values[0] &&
            values[1] &&
            new JDate(values[0].toJSDate()).getMonth() !== new JDate(values[1].toJSDate()).getMonth()
        ) {
            dateToFocus = dateToFocus.minus({ month: 1 });
        }
        const jDateToFocus = new JDate(dateToFocus.toJSDate()).startOf('month');

        this.shouldAdjustFocusDate = false;
        this.state.focusDate = this.clamp(jDateToFocus.getLDate());
    },

    next(ev) {
        if (localization.code !== 'fa_IR') {
            return super.next(ev);
        }

        ev.preventDefault();
        const { step } = this.activePrecisionLevel;
        const stepName = Object.keys(step)[0];
        const stepValue = step[stepName];
        const jDate = new JDate(this.state.focusDate.toJSDate()).add(stepName, stepValue);

        this.state.focusDate = this.clamp(jDate.getLDate());
    },
    previous(ev) {
        if (localization.code !== 'fa_IR') {
            return super.previous(ev);
        }

        ev.preventDefault();
        const { step } = this.activePrecisionLevel;
        const stepName = Object.keys(step)[0];
        const stepValue = step[stepName];
        const jDate = new JDate(this.state.focusDate.toJSDate()).subtract(stepName, stepValue);
        this.state.focusDate = this.clamp(jDate.getLDate());
    },
});

DateTimePicker.defaultProps = {
    ...DateTimePicker.defaultProps,
    daysOfWeekFormat: 'narrow',
};