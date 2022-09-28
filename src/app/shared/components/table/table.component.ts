import { AfterContentInit, AfterViewInit, Component, ContentChild, ContentChildren, EventEmitter, Input, Output, QueryList, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatColumnDef, MatHeaderRowDef, MatNoDataRow, MatRowDef, MatTable, MatTableDataSource } from '@angular/material/table';
import { TableActionsService } from '../../services/table-actions.service';
import { DeleteDialogComponent } from './delete-dialog/delete-dialog.component';

let nextId = 0;

export interface TableConfig {
  id?: string;
  title: string;
  rowDescription?: string;
  columns: string[];
  showAdd?: boolean;
  showEdit?: boolean;
  showDelete?: boolean;
}

@Component({
  selector: 'learninghouse-table',
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.scss']
})
export class TableComponent<T> implements AfterContentInit, AfterViewInit {

  private readonly _id = `${nextId++}`;

  @Input()
  dataSource!: MatTableDataSource<T>;

  @Input()
  set config(values: TableConfig) {
    this._tableConfig = {
      id: 'table_' + this._id,
      showAdd: true,
      showEdit: false,
      showDelete: false,
      ...values
    }

    if (!this.config.rowDescription) {
      this.config.rowDescription = this.config.columns[0];
    }

    if (this.config.showEdit || this.config.showDelete) {
      this.config.columns.push('actions');
    }
  }

  get config(): TableConfig {
    return this._tableConfig;
  }

  private _tableConfig = {
    title: '',
    columns: ['actions']
  };

  @ContentChildren(MatHeaderRowDef) headerRowDefs!: QueryList<MatHeaderRowDef>;
  @ContentChildren(MatRowDef) rowDefs!: QueryList<MatRowDef<T>>;
  @ContentChildren(MatColumnDef) columnDefs!: QueryList<MatColumnDef>;
  @ContentChild(MatNoDataRow) noDataRow!: MatNoDataRow;

  @ViewChild(MatTable, { static: true }) table!: MatTable<T>;

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  filter: string = '';

  constructor(public dialog: MatDialog, public actionsService: TableActionsService) { }

  ngAfterContentInit() {
    this.columnDefs.forEach(columnDef => this.table.addColumnDef(columnDef));
    this.rowDefs.forEach(rowDef => this.table.addRowDef(rowDef));
    this.headerRowDefs.forEach(headerRowDef => this.table.addHeaderRowDef(headerRowDef));
    this.table.setNoDataRow(this.noDataRow);
  }

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

  deleteRow(row: T) {
    const dialogRef = this.dialog.open(DeleteDialogComponent, {
      width: '400px'
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.actionsService.onDelete.emit({ id: this.config.id!, row: row });
      }
    })
  }

  get title_id(): string {
    return 'lh-table-title-' + this._id;
  }

}
