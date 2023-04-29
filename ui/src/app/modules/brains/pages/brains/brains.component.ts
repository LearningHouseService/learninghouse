import { AfterViewInit, Component, OnDestroy, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, map, takeUntil } from 'rxjs';
import { Role } from 'src/app/modules/auth/auth.model';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { AddEditBrainDialogComponent } from 'src/app/modules/brains/pages/brains/add-edit-brain-dialog/add-edit-brain-dialog.component';
import { BrainConfigurationModel } from 'src/app/modules/configuration/configuration.model';
import { TableActionButton, TableConfig } from 'src/app/shared/components/table/table.component';
import { TableActionsService, TableRowAction } from 'src/app/shared/services/table-actions.service';
import { BrainInfoModel } from '../../brains.model';
import { BrainsService } from '../../brains.service';

interface BrainsTableModel extends BrainInfoModel {
  estimatorTypedTranslated: string;
  needsRetraining: boolean;
  isTrained: boolean;
  hasNotEnoughData: boolean;
}


@Component({
  selector: 'app-brains',
  templateUrl: './brains.component.html'
})
export class BrainsComponent implements AfterViewInit, OnDestroy {
  private static readonly RETRAIN_BUTTON: TableActionButton = {
    id: 'retrain',
    label: 'pages.brains.actions.retrain_row_description',
    icon: 'refresh',
    conditionFlag: 'needsRetraining'
  };

  private static readonly TRAINING_BUTTON: TableActionButton = {
    id: 'training',
    label: 'pages.brains.actions.training_row_description',
    icon: 'tips_and_updates',
  };

  private static readonly PREDICTION_BUTTON: TableActionButton = {
    id: 'prediction',
    label: 'pages.brains.actions.prediction_row_description',
    svg: 'learninghouse',
    conditionFlag: 'isTrained'
  };

  dataSource = new MatTableDataSource<BrainsTableModel>();

  tableConfig: TableConfig = {
    title: 'pages.brains.common.title',
    columns: [
      { attr: 'name', label: 'pages.brains.fields.name' },
      { attr: 'estimatorTypedTranslated', label: 'pages.brains.fields.typed' },
      {
        attr: 'training_data_size',
        label: 'pages.brains.fields.training_data_size',
        icon: 'warning',
        iconTooltip: 'pages.brains.common.not_enough_training_data',
        iconConditionFlag: 'hasNotEnoughData'
      },
    ],
    rowActions: []
  }

  private destroyed = new Subject<void>();

  @ViewChild('sort') sort!: MatSort;

  constructor(
    public dialog: MatDialog,
    private router: Router,
    private brainsService: BrainsService,
    private authService: AuthService,
    private translateService: TranslateService,
    private tableActions: TableActionsService) {
    const role = this.authService.role$.getValue()
    if (role) {
      if (role.isMinimumRole(Role.TRAINER)) {
        this.tableConfig.rowActions!.push(BrainsComponent.RETRAIN_BUTTON);
      }

      if (role.isMinimumRole(Role.ADMIN)) {
        this.tableConfig.actions = [TableActionButton.ADD];
        this.tableConfig.rowActions!.push(TableActionButton.EDIT_ROW, TableActionButton.DELETE_ROW);
      }
    }

    this.tableActions.onTableAction
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onAddEdit(null))
      )
      .subscribe();

    this.tableActions.onTableRowAction
      .pipe(
        takeUntil(this.destroyed),
        map((action: TableRowAction<BrainInfoModel>) => {
          switch (action.actionId) {
            case BrainsComponent.RETRAIN_BUTTON.id:
              this.onRefresh(action.row);
              break;
            case TableActionButton.EDIT_ROW.id:
              this.onAddEdit(action.row.configuration);
              break;
            case TableActionButton.DELETE_ROW.id:
              this.onDelete(action.row.configuration);
              break;
            case BrainsComponent.TRAINING_BUTTON.id:
              this.router.navigate(['/brains/training/' + action.row.name])
                .catch((error) => console.error(error));
              break;
            case BrainsComponent.PREDICTION_BUTTON.id:
              this.router.navigate(['/brains/prediction/' + action.row.name])
                .catch((error) => console.error(error));
              break;
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
    this.brainsService.deleteBrainConfiguration(brainConfiguration)
      .pipe(
        map(() => { this.loadData(); })
      )
      .subscribe();
  }

  onRefresh(brainInfo: BrainInfoModel): void {
    this.brainsService.retrainBrain(brainInfo)
      .pipe(
        map(() => { this.loadData(); })
      )
      .subscribe();
  }

  private loadData(): void {
    this.brainsService.getBrains()
      .pipe(
        map((infos) => {
          const brains: BrainsTableModel[] = [];

          infos.forEach((info) => {
            let trained = info.trained_at != null && info.actual_versions;
            let hasEnoughData = info.training_data_size >= 10;
            let needsRetraining = !trained && hasEnoughData

            brains.push({
              ...info,
              estimatorTypedTranslated: this.translateService.instant('common.enums.estimatortype.' + info.configuration.estimator.typed),
              needsRetraining: needsRetraining,
              isTrained: trained,
              hasNotEnoughData: !hasEnoughData
            })
          })

          this.dataSource.data = brains;
        })
      )
      .subscribe()
  }

}
