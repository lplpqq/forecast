import { BASE_URL, City, WeatherData, WeatherResponse } from '@/schema';
import { PropsWithChildren, useEffect, useState } from 'react';

const fetchData = async (forCity: City) => {
  const params = new URLSearchParams({
    city: forCity.name,
    from: (new Date(2020, 1, 1)).toISOString(),
    to: (new Date(2021, 1, 1)).toISOString()
  });

  const response = await fetch(`${BASE_URL}/weather?${params}`, {
    'method': 'GET'
  });

  const results: WeatherResponse = await response.json();
  return results;
};

export interface DataViewProps {
  forCity: City | null
};

const DataView = ({
  forCity
}: PropsWithChildren<DataViewProps>) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<WeatherResponse | null>(null)

  useEffect(() => {
    if (!forCity) return;

    setLoading(true);

    fetchData(forCity).then(result => {
      setLoading(false);
      setData(result);

      console.log(result)
    });
  }, [forCity])

  if (!forCity) return <div>No data here...</div>;
  if (loading || !data) return <div>Loading...</div>

  return (
    <>
      <div className='text-lg font-semibold '>Here is the weather</div>
      <div>
        {data.data.map(dataItem => (
          <div></div>
        ))}
      </div>
    </>
  );
};

export default DataView;
