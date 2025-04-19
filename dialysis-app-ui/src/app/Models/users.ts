export interface UserCreate {
  name: string;
  email: string;
  password: string;
  role: string;
  height: number;
  sex: string;
  birth_date: Date;
}

export interface UserResponse {
  id: number;
  name: string;
  email: string;
  role: string;
  height: number;
  sex: string;
}