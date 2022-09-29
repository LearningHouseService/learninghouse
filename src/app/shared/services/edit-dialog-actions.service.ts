import { EventEmitter, Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
})
export class EditDialogActionsService {
    onSubmit = new EventEmitter<void>()
    onClose = new EventEmitter<void>()
}