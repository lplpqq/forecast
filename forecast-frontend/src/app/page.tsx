'use client';

import DataView from '@/components/DataView';
import SearchBar from '@/components/SearchBar';
import { BASE_URL, City, WeatherData, WeatherResponse, omit } from '@/schema';
import { DateInput } from '@mantine/dates';
import { useEffect, useState } from 'react';

const fetchData = async (forCity: City, dateRange: [Date, Date]) => {
  const params = new URLSearchParams({
    city: forCity.name,
    from: dateRange[0].toISOString(),
    to: dateRange[1].toISOString()
  });

  const response = await fetch(`${BASE_URL}/weather?${params}`, {
    'method': 'GET'
  });

  const results: WeatherResponse = await response.json();
  return results;
};


export default function Home() {
  const [city, setCity] = useState<City | null>(null);

  const [firstDate, setFirstDate] = useState<Date | null>(new Date(2000, 1, 1, 0, 0, 0));
  const [secondDate, setSecondDate] = useState<Date | null>(new Date(2022, 1, 1, 0, 0, 0));

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<WeatherResponse | null>(null)

  useEffect(() => {
    if (!city || firstDate === null || secondDate === null) return;

    setLoading(true);

    fetchData(city, [firstDate, secondDate]).then(result => {
      setLoading(false);

      // * Whatever, I don't really care at this point
      if (!result.data) return;

      const dataWithParsedDates: WeatherData[] = [];

      for (let item of result.data) {
        dataWithParsedDates.push({
          //@ts-ignore
          date: new Date(item.date),
          ...omit('date', item)
        })
      }

      console.log(dataWithParsedDates);

      setData({
        data: dataWithParsedDates,
        next_date: result.next_date
      });
    });
  }, [city, firstDate, secondDate])

  const dataChangeHandler = (newCity: City) => {
    setCity(newCity);
  }

  return (
    <main className="flex items-center justify-center px-8 py-16 flex-col gap-8">
      <div className='flex gap-4 flex-col items-center w-[64rem]'>
        <div className='w-full'>
          <div className='text-2xl mb-2'>Discover what it&apos;s like in...</div>
          <div className='flex flex-col items-center gap-4'>
            <div className='flex w-full gap-2'>
              <SearchBar
                dataChangeHandler={dataChangeHandler}
              />
            </div>
            <div className='w-full items-center text-md font-semibold flex gap-4 flex-col'>
              <div>Select the dates</div>

              <div className='w-fill flex flex-row gap-4 items-center'>
                <DateInput
                  value={firstDate}
                  // @ts-ignore
                  onChange={setFirstDate}
                  label="From date"
                  placeholder="The starting date..."
                />
                <DateInput
                  value={secondDate}
                  // @ts-ignore
                  onChange={setSecondDate}
                  label="To date"
                  placeholder="The end date..."
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        {(!loading && data !== null) ? <DataView
          data={data}
        /> : null}
      </div>
    </main >
  );
}
