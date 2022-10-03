import { EventEmitter, Injectable } from "@angular/core";

export interface TableAction {
    tableId: string;
    actionId: string;
}

export interface TableRowAction<T> extends TableAction {
    row: T;
}

@Injectable({
    providedIn: 'root'
})
export class TableActionsService {
    onTableAction = new EventEmitter<TableAction>();
    onTableRowAction = new EventEmitter<TableRowAction<any>>();
}