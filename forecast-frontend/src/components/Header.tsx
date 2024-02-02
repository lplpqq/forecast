import { PropsWithChildren } from 'react';

export interface HeaderProps {

};

const Header = ({ }: PropsWithChildren<HeaderProps>) => {
  return (
    <div className='flex flex-row px-8 py-4 justify-start bg-yellow-500'>
      <div
        className='font-semibold text-xl'
      >
        Weather Forecast
      </div>
    </div>
  );
};

export default Header;
