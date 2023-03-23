import { Component } from '@angular/core';

import { Image, User } from '@app/_models';
import { AccountService } from '@app/_services';
import { first } from 'rxjs/operators';
import { environment } from '@environments/environment';

@Component({ templateUrl: 'home.component.html' })
export class HomeComponent {
    user: User | null;
    selectedFile: File | null = null;
    fileName: string = '';
    fileSize: string = '';
    showFileError: boolean = false;
    Images:Image[]=[];
    selectedTitle:string=''
    selectedDesc:string='';
    apiUrl:string=environment.apiUrl;
    clickedImage:string='-1';
    selected_grid_position:string="0";

    constructor(private accountService: AccountService) {
        this.user = this.accountService.userValue;
       
    }
    ngOnInit() {
      if(this.user)
        {
           this.accountService.getImages(this.user.id||"").pipe(first()).subscribe(images=>{
            console.log(images);
            for(let i=0;i<16;i++)
            {
              let inIf=false;
              for(let image of images)
              {
                  if(image.grid_position==i.toString())
                  {
                      this.Images.push(image);
                      inIf=true;
                  }
              }
              if(!inIf)
                {
                  this.Images.push({"grid_position":i.toString()});
                  console.log(this.Images);
                }
            }
            console.log(this.Images);
          });
           console.log(this.Images);
        }
  }
    
    onFileInputChange(event: any): void {
        this.selectedFile = event.target.files[0];

        if (this.selectedFile && this.isImage(this.selectedFile)) {
            this.selectedFile = this.selectedFile;
            this.fileName = this.selectedFile.name;
            this.fileSize = this.formatFileSize(this.selectedFile.size);
            this.showFileError = false;
        } else {
            this.selectedFile = null;
            this.fileName = '';
            this.fileSize = '';
            this.showFileError = true;
        }
      }
      onTitleChange(event:any)
      {
        this.selectedTitle=event.target.value;
      }
      onDescChange(event:any)
      {
        this.selectedDesc=event.target.value;
      }
      onGridChange(event:any)
      {
        this.selected_grid_position=event.target.value;
      }

      isImage(file: File): boolean {
        const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        return validImageTypes.includes(file.type);
      }

      imageClick(grid_position:string)
      {
          this.clickedImage=grid_position;
          console.log(this.clickedImage);

      }

      removeImage(grid_position:string)
      {
        this.accountService.removeImages(this.user?.id||'',grid_position).subscribe(response=>{
            alert('Image Deleted');
            window.location.reload();
        },
        error=>{
          alert('Image Not Deleted');
        })
      }
    
      uploadFile(): void {
        if (!this.selectedFile) {
          this.showFileError = true;
          return;
        }
        if(this.selectedTitle=="")
        {
          alert('Please Add a Title');
          return ;
        }
        if(this.selectedDesc=="")
        {
          alert('Please Add a Description');
          return ;
        }
        if(this.selected_grid_position=="")
        {
          alert('Please select a grid positon');
          return ;
        }
    
        this.showFileError = false;
        if (this.user?.id)
        {
        this.accountService.uploadImage(this.user.id,this.selectedFile,this.selectedTitle,this.selectedDesc,this.selected_grid_position).subscribe(
          response => {
            alert('File uploaded successfully');
            window.location.reload();
          },
          error => {
            alert('File upload failed');
            this.showFileError=true;
          }
        );
        }
    }
    
      removeSelectedFile(): void {
        this.selectedFile = null;
        this.fileName = '';
        this.fileSize = '';
      }
      formatFileSize(size: number): string {
        if (size < 1024) {
          return size + ' B';
        } else if (size < 1024 * 1024) {
          return (size / 1024).toFixed(1) + ' KB';
        } else {
          return (size / (1024 *1024)).toFixed(1) + ' MB';
        }
    }
    
}