import { AfterViewInit, Component, OnDestroy, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map, Subject, takeUntil } from 'rxjs';
import { APIKeyModel } from 'src/app/shared/models/auth.model';
import { TableActionsService, TableDeleteAction } from 'src/app/shared/services/table-actions.service';
import { AuthService } from '../../auth.service';
import { AddAPIKeyDialogComponent } from './add-apikey-dialog/add-apikey-dialog.component';

interface APIKeyTableModel extends APIKeyModel {
  roleTranslated: string;
}

@Component({
  selector: 'learninghouse-apikeys',
  templateUrl: './apikeys.component.html',
  styleUrls: ['./apikeys.component.scss']
})
export class APIKeysComponent implements AfterViewInit, OnDestroy {

  dataSource = new MatTableDataSource<APIKeyTableModel>();

  tableConfig = {
    title: 'pages.auth.apikeys.common.title',
    columns: [
      { attr: 'description', label: 'pages.auth.apikeys.columns.description' },
      { attr: 'roleTranslated', label: 'pages.auth.apikeys.columns.role' }
    ],
    showDelete: true
  }

  private destroyed = new Subject<void>();

  @ViewChild('sort') sort!: MatSort;

  constructor(public dialog: MatDialog, private authService: AuthService, private translateService: TranslateService, private tableActions: TableActionsService) {

    this.tableActions.onAdd.pipe(
      takeUntil(this.destroyed),
      map(() => this.onAdd())
    ).subscribe()

    this.tableActions.onDelete.pipe(
      takeUntil(this.destroyed),
      map((action: TableDeleteAction<APIKeyTableModel>) => action.row),
      map((apikey: APIKeyModel) => this.onDelete(apikey))
    ).subscribe()
  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  ngAfterViewInit(): void {
    this.loadData();
    this.dataSource.sort = this.sort;
  }

  loadData(): void {
    this.authService.getAPIKeys()
      .pipe(
        map((apikeys) => {
          const translatedAPIKeys: APIKeyTableModel[] = [];
          apikeys.forEach((apikey) => {
            translatedAPIKeys.push({
              ...apikey,
              roleTranslated: this.translateService.instant('common.role.' + apikey.role)
            });
          })
          this.dataSource.data = translatedAPIKeys;
        })
      )
      .subscribe()
  }

  onAdd(): void {
    const dialogRef = this.dialog.open(AddAPIKeyDialogComponent, {
      width: '480px'
    });

    dialogRef.afterClosed().subscribe((apikey: APIKeyModel | null) => {
      if (apikey) {
        this.loadData();
      }
    });
  }

  onDelete(apikey: APIKeyModel): void {
    this.authService.deleteAPIKey(apikey.description)
      .pipe(
        map(() => {
          this.loadData();
        })
      )
      .subscribe()
  }
}
