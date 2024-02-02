import { BASE_URL, City, WeatherData, WeatherResponse } from '@/schema';
import { Table } from '@mantine/core';
import { PropsWithChildren, useEffect, useState } from 'react';

function omit(key: any, obj: any) {
  const { [key]: omitted, ...rest } = obj;
  return rest;
}

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

export interface DataViewProps {
  forCity: City | null
  dateRange: [Date | null, Date | null]
};

const DataView = ({
  dateRange
}: PropsWithChildren<DataViewProps>) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<WeatherResponse | null>(null)

  useEffect(() => {
    if (!forCity || dateRange[0] === null || dateRange[1] === null) return;

    setLoading(true);

    fetchData(forCity, dateRange).then(result => {
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
  }, [forCity])

  if (!forCity) return <div>No data here...</div>;
  if (dateRange[0] === null || dateRange[1] === null) return <div>Please select the dates...</div>;
  if (loading || !data) return <div>Loading...</div>

  return (
    <>
      <div className='text-lg font-semibold '>Here is the weather</div>
      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Date</Table.Th>
            <Table.Th>Tempreature</Table.Th>
            <Table.Th>Pressure</Table.Th>
            <Table.Th>Wind Speed</Table.Th>
            <Table.Th>Wind Direction</Table.Th>
            <Table.Th>Humidity</Table.Th>
            <Table.Th>Precipitation</Table.Th>
            <Table.Th>Snow</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {data.data.map(dataItem => (
            <Table.Tr key={dataItem.date.toString()}>
              <Table.Td>{dataItem.date.toISOString().split('T')[0]}</Table.Td>
              <Table.Td>{dataItem.temperature} &deg;c</Table.Td>
              <Table.Td>{(dataItem.pressure / 1000).toFixed(4)} atm</Table.Td>
              <Table.Td>{dataItem.wind_speed} m/s</Table.Td>
              <Table.Td>{dataItem.wind_direction}&deg;</Table.Td>
              <Table.Td>{dataItem.humidity}%</Table.Td>
              <Table.Td>{dataItem.precipitation} mm</Table.Td>
              <Table.Td>{dataItem.snow} mm</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </>
  );
};

export default DataView;
