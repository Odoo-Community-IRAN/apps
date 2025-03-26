/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { patch } from "@web/core/utils/patch";

import { _t } from "@web/core/l10n/translation";
import { ColorList } from "@web/core/colorlist/colorlist";
import { evaluateBooleanExpr } from "@web/core/py_js/py";
import { registry } from "@web/core/registry";
import { useTooltip } from "@web/core/tooltip/tooltip_hook";
import { useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";
import { useRecordObserver } from "@web/model/relational_model/utils";
import { fileTypeMagicWordMap, imageCacheKey } from "@web/views/fields/image/image_field";
import { useViewCompiler } from "@web/views/view_compiler";
import { getFormattedValue } from "./format_utils";

import {
    KANBAN_BOX_ATTRIBUTE,
    KANBAN_MENU_ATTRIBUTE,
    KANBAN_TOOLTIP_ATTRIBUTE,
} from "@web/views/kanban/kanban_arch_parser";


import { Component, onMounted, onWillUpdateProps, useRef, useState } from "@odoo/owl";
const { COLORS } = ColorList;

const formatters = registry.category("formatters");

// These classes determine whether a click on a record should open it.
export const CANCEL_GLOBAL_CLICK = ["a", ".dropdown", ".oe_kanban_action", "[data-bs-toggle]"].join(
    ","
);
const ALLOW_GLOBAL_CLICK = [".oe_kanban_global_click", ".oe_kanban_global_click_edit"].join(",");

/**
 * Returns the class name of a record according to its color.
 */
function getColorClass(value) {
    return `oe_kanban_color_${getColorIndex(value)}`;
}

export function leftPad(number, targetLength) {
      var output = number + '';
      while (output.length < targetLength) {
          output = '0' + output;
      }
      return output;
}

/**
 * Returns the index of a color determined by a given record.
 */
function getColorIndex(value) {
    if (typeof value === "number") {
        return Math.round(value) % COLORS.length;
    } else if (typeof value === "string") {
        const charCodeSum = [...value].reduce((acc, _, i) => acc + value.charCodeAt(i), 0);
        return charCodeSum % COLORS.length;
    } else {
        return 0;
    }
}

/**
 * Returns the proper translated name of a record color.
 */
function getColorName(value) {
    return COLORS[getColorIndex(value)];
}

/**
 * Returns a "raw" version of the field value on a given record.
 *
 * @param {Record} record
 * @param {string} fieldName
 * @returns {any}
 */
export function getRawValue(record, fieldName) {
    const field = record.fields[fieldName];
    const value = record.data[fieldName];
    switch (field.type) {
        case "one2many":
        case "many2many": {
            return value.count ? value.currentIds : [];
        }
        case "many2one": {
            return (value && value[0]) || false;
        }
        case "date":
        case "datetime": {
            return value && value.toISO();
        }
        default: {
            return value;
        }
    }
}

/**
 * Returns a formatted version of the field value on a given record.
 *
 * @param {Record} record
 * @param {string} fieldName
 * @returns {string}
 */
function getValue(record, fieldName) {
    const field = record.fields[fieldName];
    const value = record.data[fieldName];
    const formatter = formatters.get(field.type, String);
    
    if (field.type == "datetime") {
      
      const ressult = formatter(value, { field, data: record.data });

      if(!ressult || ressult == ''){
            return ressult
      }

      let jressult_str = "";

      if(ressult.split(' ')[1]){

            if(ressult.split(' ')[0].split('/')[2]){
                  const gressult = ressult.split(' ')[0].split('/');
                  const jressult = farvardin.gregorianToSolar(parseInt(gressult[0]) , parseInt(gressult[1]) , parseInt(gressult[2]));
                  jressult_str =  `${jressult[0]}/${leftPad(jressult[1], 2)}/${leftPad(jressult[2], 2)} ${ressult.split(' ')[1]}`;
            }else if(ressult.split(' ')[0].split('-')[2]){
                  const gressult = ressult.split(' ')[0].split('-');
                  const jressult = farvardin.gregorianToSolar(parseInt(gressult[0]) , parseInt(gressult[1]) , parseInt(gressult[2]));
                  jressult_str =  `${jressult[0]}-${leftPad(jressult[1], 2)}-${leftPad(jressult[2], 2)} ${ressult.split(' ')[1]}`;
            }
      }
      else{

            if(ressult.split('/')[2]){
                  const gressult = ressult.split('/');
                  const jressult = farvardin.gregorianToSolar(parseInt(gressult[0]) , parseInt(gressult[1]) , parseInt(gressult[2]));
                  jressult_str =  `${jressult[0]}/${leftPad(jressult[1], 2)}/${leftPad(jressult[2], 2)}`;
            }else if(ressult.split('-')[2]){
                  const gressult = ressult.split('-');
                  const jressult = farvardin.gregorianToSolar(parseInt(gressult[0]) , parseInt(gressult[1]) , parseInt(gressult[2]));
                  jressult_str =  `${jressult[0]}-${leftPad(jressult[1], 2)}-${leftPad(jressult[2], 2)}`;
            }

      }

      return jressult_str;


      }
    return formatter(value, { field, data: record.data });
}

export function getFormattedRecord(record) {
    const formattedRecord = {
        id: {
            value: record.resId,
            raw_value: record.resId,
        },
    };

    for (const fieldName of record.fieldNames) {
        formattedRecord[fieldName] = {
            value: getValue(record, fieldName),
            raw_value: getRawValue(record, fieldName),
        };
    }
    return formattedRecord;
}

/**
 * Returns the image URL of a given field on the record.
 *
 * @param {Record} record
 * @param {string} [model] model name
 * @param {string} [field] field name
 * @param {number | [number, ...any[]]} [idOrIds] id or array
 *      starting with the id of the desired record.
 * @param {string} [placeholder] fallback when the image does not
 *  exist
 * @returns {string}
 */
export function getImageSrcFromRecordInfo(record, model, field, idOrIds, placeholder) {
    const id = (Array.isArray(idOrIds) ? idOrIds[0] : idOrIds) || null;
    const isCurrentRecord =
        record.resModel === model && (record.resId === id || (!record.resId && !id));
    const fieldVal = record.data[field];
    if (isCurrentRecord && fieldVal && !isBinSize(fieldVal)) {
        // Use magic-word technique for detecting image type
        const type = fileTypeMagicWordMap[fieldVal[0]];
        return `data:image/${type};base64,${fieldVal}`;
    } else if (placeholder && (!model || !field || !id || !fieldVal)) {
        // Placeholder if either the model, field, id or value is missing or null.
        return placeholder;
    } else {
        // Else: fetches the image related to the given id.
        return url("/web/image", {
            model,
            field,
            id,
            unique: imageCacheKey(record.data.write_date),
        });
    }
}

function isBinSize(value) {
    return /^\d+(\.\d*)? [^0-9]+$/.test(value);
}

/**
 * Checks if a html content is empty. If there are only formatting tags
 * with style attributes or a void content. Famous use case is
 * '<p style="..." class=".."><br></p>' added by some web editor(s).
 * Note that because the use of this method is limited, we ignore the cases
 * like there's one <img> tag in the content. In such case, even if it's the
 * actual content, we consider it empty.
 *
 * @param {string} innerHTML
 * @returns {boolean} true if no content found or if containing only formatting tags
 */
export function isHtmlEmpty(innerHTML = "") {
    const div = Object.assign(document.createElement("div"), { innerHTML });
    return div.innerText.trim() === "";
}

patch(KanbanRecord.prototype, {
    setup() {
        this.evaluateBooleanExpr = evaluateBooleanExpr;
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.user = useService("user");

        const { Compiler, templates } = this.props;
        const ViewCompiler = Compiler || this.constructor.Compiler;

        this.templates = useViewCompiler(ViewCompiler, templates);

        if (this.constructor.KANBAN_MENU_ATTRIBUTE in templates) {
            this.showMenu = true;
        }

        if (KANBAN_TOOLTIP_ATTRIBUTE in templates) {
            useTooltip("root", {
                info: { ...this, record: getFormattedRecord(this.props.record) },
                template: this.templates[KANBAN_TOOLTIP_ATTRIBUTE],
            });
        }

        this.dataState = useState({ record: {}, widget: {} });
        this.createWidget(this.props);
        onWillUpdateProps(this.createWidget);
        useRecordObserver((record) =>
            Object.assign(this.dataState.record, getFormattedRecord(record))
        );
        this.rootRef = useRef("root");
        onMounted(() => {
            // FIXME: this needs to be changed to an attribute on the root node...
            this.allowGlobalClick = !!this.rootRef.el.querySelector(ALLOW_GLOBAL_CLICK);
        });
    },
    getFormattedValue(fieldId) {
        const { archInfo, record } = this.props;
        const { attrs, name } = archInfo.fieldNodes[fieldId];
        return getFormattedValue(record, name, attrs);
    }
});