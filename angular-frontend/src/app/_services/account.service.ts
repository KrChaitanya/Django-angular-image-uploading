import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '@environments/environment';
import { Image, User } from '@app/_models';
import { Data } from '@app/_models/data';

@Injectable({ providedIn: 'root' })
export class AccountService {
    private userSubject: BehaviorSubject<User | null>;
    public user: Observable<User | null>;

    constructor(
        private router: Router,
        private http: HttpClient
    ) {
        this.userSubject = new BehaviorSubject(JSON.parse(localStorage.getItem('user')!));
        this.user = this.userSubject.asObservable();
    }

    public get userValue() {
        return this.userSubject.value;
    }

    login(username: string, password: string) {
        return this.http.post<Data>(`${environment.apiUrl}/login/`, { username, password })
            .pipe(map(dat => {
                var user:User=dat.user||{};
                if(user)
                {
                    user.token=dat.access;
                }
                console.log(user);
                // store user details and jwt token in local storage to keep user logged in between page refreshes
                localStorage.setItem('user', JSON.stringify(user));
                this.userSubject.next(user);
                return user;
            }));
    }

    logout() {
        // remove user from local storage and set current user to null
        localStorage.removeItem('user');
        this.userSubject.next(null);
        this.router.navigate(['/account/login']);
    }

    register(user: User) {
        return this.http.post(`${environment.apiUrl}/register/`, user);
    }

    

    getById(id: string) {
        return this.http.get<User>(`${environment.apiUrl}/users/${id}`);
    }

    uploadImage(id:string,image: File,title:string,description:string,grid_position:string): Observable<any> {
        const formData = new FormData();
        formData.append('image', image);
        formData.append('user',this.userValue?.id||'-1');
        formData.append('upload_date',new Date().toLocaleDateString());
        formData.append('title',title);
        formData.append('grid_position',grid_position);
        formData.append('description',description);
        console.log(title,description);

        return this.http.post(`${environment.apiUrl}/users/${id}/images/`, formData).pipe(
            map(response => {
                return response;
            })
        );
    }
    getImages(id:string)
    {
        return this.http.get<Image[]>(`${environment.apiUrl}/users/${id}/images/`);
    }
    removeImages(user_id:string,grid_position:string)
    {
        return this.http.delete(`${environment.apiUrl}/users/${user_id}/images/${grid_position}/`).pipe(
            map(response => {
                return response;
            })
        );
    }
}