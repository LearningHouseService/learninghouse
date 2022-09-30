import { AfterViewInit, Component, OnDestroy, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map, Subject, takeUntil } from 'rxjs';
import { SensorModel, SensorType } from 'src/app/shared/models/configuration.model';
import { TableActionsService, TableEditAction } from 'src/app/shared/services/table-actions.service';
import { ConfigurationService } from '../../configuration.service';
import { AddEditSensorDialogComponent } from './add-edit-sensor-dialog/add-edit-sensor-dialog.component';

interface SensorTableModel {
  name: string;
  typed: SensorType;
  typedTranslated: string;
}

@Component({
  selector: 'app-sensors',
  templateUrl: './sensors.component.html',
  styleUrls: ['./sensors.component.scss']
})
export class SensorsComponent implements AfterViewInit, OnDestroy {

  dataSource = new MatTableDataSource<SensorTableModel>();

  tableConfig = {
    title: 'pages.configuration.sensors.common.title',
    columns: [
      { attr: 'name', label: 'pages.configuration.sensors.columns.name' },
      { attr: 'typedTranslated', label: 'pages.configuration.sensors.columns.typed' }
    ],
    showEdit: true,
    showDelete: true
  }

  private destroyed = new Subject<void>();

  @ViewChild('sort') sort!: MatSort;

  constructor(public dialog: MatDialog, private configService: ConfigurationService,
    private translateService: TranslateService, private tableActions: TableActionsService) {

    this.tableActions.onAdd
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onAdd())
      )
      .subscribe();

    this.tableActions.onEdit
      .pipe(
        takeUntil(this.destroyed),
        map((action: TableEditAction<SensorTableModel>) => { return action.row }),
        map((sensor: SensorTableModel) => this.onEdit({ name: sensor.name, typed: sensor.typed as SensorType }))
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

  loadData(): void {
    this.configService.getSensors()
      .pipe(
        map((sensors) => {
          const translatedSensors: SensorTableModel[] = [];
          sensors.forEach((sensor) => {
            translatedSensors.push({
              name: sensor.name,
              typed: sensor.typed,
              typedTranslated: this.translateService.instant('common.sensortype.' + sensor.typed)
            });
          });

          this.dataSource.data = translatedSensors;

        })
      )
      .subscribe()
  }

  onAdd(): void {
    const dialogRef = this.dialog.open(AddEditSensorDialogComponent, {
      width: '480px'
    });

    dialogRef.afterClosed().subscribe((sensor: SensorModel | null) => {
      if (sensor) {
        this.loadData();
      }
    });
  }

  onEdit(sensor: SensorModel): void {
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

}
