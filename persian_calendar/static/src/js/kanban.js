/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { evaluateBooleanExpr } from "@web/core/py_js/py";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useRecordObserver } from "@web/model/relational_model/utils";
import { useViewCompiler } from "@web/views/view_compiler";
import { getFormattedValue } from "./format_utils";
import { onWillUpdateProps, useRef, useState } from "@odoo/owl";

const formatters = registry.category("formatters");

export function leftPad(number, targetLength) {
    var output = number + '';
    while (output.length < targetLength) {
        output = '0' + output;
    }
    return output;
}
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
      }else{
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
patch(KanbanRecord.prototype, {
    setup() {
        this.evaluateBooleanExpr = evaluateBooleanExpr;
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.notification = useService("notification");

        const { archInfo, Compiler, templates } = this.props;
        const ViewCompiler = Compiler || this.constructor.Compiler;
        const isLegacy = archInfo.isLegacyArch;

        this.templates = useViewCompiler(ViewCompiler, templates, { isLegacy });

        this.menuTemplateName = this.props.archInfo.isLegacyArch
            ? this.constructor.LEGACY_KANBAN_MENU_ATTRIBUTE
            : this.constructor.KANBAN_MENU_ATTRIBUTE;
        this.showMenu = this.menuTemplateName in templates;

        this.dataState = useState({ record: {}, widget: {} });
        this.createWidget(this.props);
        onWillUpdateProps(this.createWidget);
        useRecordObserver((record) =>
            Object.assign(this.dataState.record, getFormattedRecord(record))
        );
        this.rootRef = useRef("root");
    },
    getFormattedValue(fieldId) {
        const { archInfo, record } = this.props;
        const { name } = archInfo.fieldNodes[fieldId];
        return getFormattedValue(record, name, archInfo.fieldNodes[fieldId]);
    }
});