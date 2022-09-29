import { AfterViewInit, Component, Input, ViewChild } from '@angular/core';
import { MediaObserver } from '@angular/flex-layout';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { TableActionsService } from '../../services/table-actions.service';
import { DeleteDialogComponent } from './delete-dialog/delete-dialog.component';

let nextId = 0;

export interface TableColumn {
  attr: string;
  label: string;
}

export interface TableConfig {
  id?: string;
  title: string;
  rowDescription?: string;
  columns: TableColumn[];
  showAdd?: boolean;
  showEdit?: boolean;
  showDelete?: boolean;
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
      showAdd: true,
      showEdit: false,
      showDelete: false,
      ...values
    }

    if (!this.config.rowDescription) {
      this.config.rowDescription = this.config.columns[0].attr;
    }

    this.config.columns.forEach((column) => {
      this.displayColumns.push(column.attr)
    });

    if (this.config.showEdit || this.config.showDelete) {
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

  constructor(public dialog: MatDialog,
    public actionsService: TableActionsService,
    public media$: MediaObserver) { }


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
