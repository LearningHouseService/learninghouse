import { AfterViewInit, Component, OnDestroy, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map, Subject, takeUntil } from 'rxjs';
import { TableActionButton, TableConfig } from 'src/app/shared/components/table/table.component';
import { BrainConfigurationModel } from 'src/app/shared/models/configuration.model';
import { TableActionsService, TableRowAction } from 'src/app/shared/services/table-actions.service';
import { ConfigurationService } from '../../configuration.service';
import { AddEditBrainDialogComponent } from './add-edit-brain-dialog/add-edit-brain-dialog.component';

interface BrainConfigurationTableModel extends BrainConfigurationModel {
  estimatorTypedTranslated: string;
}

@Component({
  selector: 'app-brains',
  templateUrl: './brains.component.html',
  styleUrls: ['./brains.component.scss']
})
export class BrainsComponent implements AfterViewInit, OnDestroy {

  dataSource = new MatTableDataSource<BrainConfigurationTableModel>();

  tableConfig: TableConfig = {
    title: 'pages.configuration.brains.common.title',
    columns: [
      { attr: 'name', label: 'pages.configuration.brains.fields.name' },
      { attr: 'estimatorTypedTranslated', label: 'pages.configuration.brains.fields.typed' },
      { attr: 'dependent', label: 'pages.configuration.brains.fields.dependent' }
    ],
    actions: [TableActionButton.ADD],
    rowActions: [TableActionButton.EDIT_ROW, TableActionButton.DELETE_ROW]
  }


  private destroyed = new Subject<void>();

  @ViewChild('sort') sort!: MatSort;

  constructor(public dialog: MatDialog, private configService: ConfigurationService,
    private translateService: TranslateService, private tableActions: TableActionsService) {

    this.tableActions.onTableAction
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onAddEdit(null))
      )
      .subscribe();

    this.tableActions.onTableRowAction
      .pipe(
        takeUntil(this.destroyed),
        map((action: TableRowAction<BrainConfigurationModel>) => {
          if (action.actionId === TableActionButton.EDIT_ROW.id) {
            this.onAddEdit(action.row);
          } else {
            this.onDelete(action.row);
          }
        })
      )
      .subscribe();
  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  ngAfterViewInit(): void {
    this.loadData();
    this.dataSource.sort = this.sort;
  }


  onAddEdit(brainConfiguration: BrainConfigurationModel | null): void {
    const dialogRef = this.dialog.open(AddEditBrainDialogComponent, {
      width: '480px',
      data: brainConfiguration
    });

    dialogRef.afterClosed().subscribe((brainConfiguration: BrainConfigurationModel | null) => {
      if (brainConfiguration) {
        this.loadData();
      }
    });
  }

  onDelete(brainConfiguration: BrainConfigurationModel): void {
    this.configService.deleteBrainConfiguration(brainConfiguration)
      .pipe(
        map(() => {
          this.loadData();
        })
      )
      .subscribe()
  }

  loadData(): void {
    this.configService.getBrains()
      .pipe(
        map((configurations) => {
          const translatedConfigurations: BrainConfigurationTableModel[] = [];
          configurations.forEach((configuration) => {
            translatedConfigurations.push({
              ...configuration,
              estimatorTypedTranslated: this.translateService.instant('common.enums.estimatortype.' + configuration.estimator.typed)
            });
          });

          this.dataSource.data = translatedConfigurations;

        })
      )
      .subscribe()
  }
}
