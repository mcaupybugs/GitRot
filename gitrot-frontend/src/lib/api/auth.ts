import { apiClient } from "./client";

export interface UserAuthData {
  email: string;
  name: string;
  image: string;
  provider: string;
  provider_id: string;
}

export interface UserAuthResponse {
  user_id: string;
  is_new: boolean;
  email: string;
  name: string;
  image: string;
}

export const authApi = {
  async registerOrLogin(userData: UserAuthData): Promise<UserAuthResponse> {
    return apiClient.post<UserAuthResponse>(
      "/auth/register-or-login",
      userData
    );
  },

  async getUserProfile(userId: string): Promise<UserAuthResponse> {
    return apiClient.post<UserAuthResponse>(`/users/${userId}`);
  },

  async updateUserProfile(
    userId: string,
    data: Partial<UserAuthResponse>
  ): Promise<UserAuthResponse> {
    return apiClient.put<UserAuthResponse>(`/users/${userId}`, data);
  },
};
