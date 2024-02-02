export const BASE_URL = `http://localhost:8080`

export interface City {
  name: string;
  country: string;
}

export interface SearchCitiesResponse {
  cities: City[]
}

export interface WeatherData {
  date: Date
  temperature: number
  pressure: number
  wind_speed: number
  wind_direction: number
  humidity: number
  precipitation: number | null
  snow: number | null
}

export interface WeatherResponse {
  data: WeatherData[]
  next_date: Date | null
}
