import { WeatherResponse } from '@/schema';
import { Table } from '@mantine/core';
import { PropsWithChildren } from 'react';

export interface DataViewProps {
  data: WeatherResponse
};

const DataView = ({
  data
}: PropsWithChildren<DataViewProps>) => {
  if (!data) return <div>No data</div>

  return (
    <>
      <div className='text-lg font-semibold '>Weather history</div>
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
              <Table.Td>{dataItem.temperature.toFixed(1)} &deg;c</Table.Td>
              <Table.Td>{(dataItem.pressure / 1000).toFixed(0)} atm</Table.Td>
              <Table.Td>{dataItem.wind_speed.toFixed(2)} m/s</Table.Td>
              <Table.Td>{dataItem.wind_direction.toFixed(0)}&deg;</Table.Td>
              <Table.Td>{dataItem.humidity.toFixed(0)}%</Table.Td>
              <Table.Td>{dataItem.precipitation?.toFixed(0)} mm</Table.Td>
              <Table.Td>{dataItem.snow?.toFixed(0)} mm</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </>
  );
};

export default DataView;
