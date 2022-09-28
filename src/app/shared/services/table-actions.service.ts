import { EventEmitter, Injectable } from "@angular/core";

interface TableAction {
    id: string;
}

export interface TableAddAction extends TableAction { }

export interface TableDeleteAction<T> extends TableAction {
    row: T;
}

export interface TableEditAction<T> extends TableAction {
    row: T;
}


@Injectable({
    providedIn: 'root'
})
export class TableActionsService {
    onAdd = new EventEmitter<TableAddAction>();
    onEdit = new EventEmitter<TableEditAction<any>>();
    onDelete = new EventEmitter<TableDeleteAction<any>>();
}