import { AfterViewInit, Component, Input, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { BreakpointService } from '../../services/breakpoint.service';
import { TableActionsService } from '../../services/table-actions.service';
import { DeleteDialogComponent } from './delete-dialog/delete-dialog.component';

let nextId = 0;

export interface TableColumn {
  attr: string;
  label: string;
}

export class TableActionButton {
  static readonly ADD = new TableActionButton('add', 'components.table.actions.add', 'add');

  static readonly EDIT_ROW = new TableActionButton('edit', 'components.table.actions.edit_row_description', 'edit');

  static readonly DELETE_ROW = new TableActionButton('delete', 'components.table.actions.delete_row_description', 'delete');

  constructor(public id: string,
    public label: string,
    public icon?: string,
    public svg?: string) { }
}


export interface TableConfig {
  title: string;
  columns: TableColumn[];

  id?: string;
  rowDescription?: string;
  actions?: TableActionButton[];
  rowActions?: TableActionButton[];
}

@Component({
  selector: 'learninghouse-table',
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.scss']
})
export class TableComponent<T> implements AfterViewInit {

  private readonly _id = `${nextId++}`;

  @Input()
  dataSource!: MatTableDataSource<T>;

  displayColumns: string[] = [];

  @Input()
  set config(values: TableConfig) {
    this._tableConfig = {
      id: 'table_' + this._id,
      actions: [],
      rowActions: [],
      ...values
    }

    if (!this.config.rowDescription) {
      this.config.rowDescription = this.config.columns[0].attr;
    }

    this.config.columns.forEach((column) => {
      this.displayColumns.push(column.attr)
    });

    if (this.config.rowActions) {
      this.displayColumns.push('actions');
    }
  }

  get config(): TableConfig {
    return this._tableConfig;
  }

  private _tableConfig: TableConfig = {
    title: '',
    columns: []
  };


  @ViewChild(MatPaginator) paginator!: MatPaginator;

  filter: string = '';

  constructor(
    public dialog: MatDialog,
    public actionsService: TableActionsService,
    public breakpoints: BreakpointService) { }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
  }

  doFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLocaleLowerCase();
  }

  clearFilter() {
    this.dataSource.filter = '';
    this.filter = '';
  }

  onRowAction(actionId: string, row: T) {
    if (actionId === TableActionButton.DELETE_ROW.id) {
      const dialogRef = this.dialog.open(DeleteDialogComponent, {
        width: '400px'
      });

      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          this.actionsService.onTableRowAction.emit({ tableId: this.config.id!, actionId: actionId, row: row });
        }
      })
    } else {
      this.actionsService.onTableRowAction.emit({ tableId: this.config.id!, actionId: actionId, row: row })
    }
  }

  get title_id(): string {
    return 'lh-table-title-' + this._id;
  }

}
