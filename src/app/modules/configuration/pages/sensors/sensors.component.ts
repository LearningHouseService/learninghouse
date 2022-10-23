import { AfterViewInit, Component, OnDestroy, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map, Subject, takeUntil } from 'rxjs';
import { TableActionButton, TableConfig } from 'src/app/shared/components/table/table.component';
import { SensorModel } from 'src/app/shared/models/configuration.model';
import { TableActionsService, TableRowAction } from 'src/app/shared/services/table-actions.service';
import { ConfigurationService } from '../../configuration.service';
import { AddEditSensorDialogComponent } from './add-edit-sensor-dialog/add-edit-sensor-dialog.component';

interface SensorTableModel extends SensorModel {
  typedTranslated: string;
}

@Component({
  selector: 'app-sensors',
  templateUrl: './sensors.component.html',
  styleUrls: ['./sensors.component.scss']
})
export class SensorsComponent implements AfterViewInit, OnDestroy {

  dataSource = new MatTableDataSource<SensorTableModel>();

  tableConfig: TableConfig = {
    title: 'pages.configuration.sensors.common.title',
    columns: [
      { attr: 'name', label: 'pages.configuration.sensors.columns.name' },
      { attr: 'typedTranslated', label: 'pages.configuration.sensors.columns.typed' }
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
        map((action: TableRowAction<SensorModel>) => {
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

  onAddEdit(sensor: SensorModel | null): void {
    const dialogRef = this.dialog.open(AddEditSensorDialogComponent, {
      width: '480px',
      data: sensor
    });

    dialogRef.afterClosed().subscribe((sensor: SensorModel | null) => {
      if (sensor) {
        this.loadData();
      }
    });
  }

  onDelete(sensor: SensorModel): void {
    this.configService.deleteSensor(sensor)
      .pipe(
        map(() => {
          this.loadData();
        })
      )
      .subscribe()
  }

  loadData(): void {
    this.configService.getSensors()
      .pipe(
        map((sensors) => {
          const translatedSensors: SensorTableModel[] = [];
          sensors.forEach((sensor) => {
            translatedSensors.push({
              ...sensor,
              typedTranslated: this.translateService.instant('common.enums.sensortype.' + sensor.typed)
            });
          });

          this.dataSource.data = translatedSensors;

        })
      )
      .subscribe()
  }

}
