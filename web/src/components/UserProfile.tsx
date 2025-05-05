import React from 'react';
import Image from 'next/image';

interface UserProfileProps {
  avatar: string;
  nickname: string;
  id: string;
  server: string;
  squadPower: number;
  nikkeObtained: number;
  costume: number;
  nikkeDistribution: string[];
}

const UserProfile: React.FC<UserProfileProps> = ({
  avatar,
  nickname,
  id,
  server,
  squadPower,
  nikkeObtained,
  costume,
  nikkeDistribution,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 w-96">
      <div className="flex items-center justify-between border-b pb-4 mb-4">
        <div className="flex items-center">
          <Image
            src={avatar}
            alt="User Avatar"
            width={64}
            height={64}
            className="rounded-full border-2 border-gray-300"
          />
          <div className="ml-4">
            <h2 className="text-lg font-bold">{nickname}</h2>
            <p className="text-sm text-gray-500">ID: {id}</p>
            <p className="text-sm text-gray-500">Server: {server}</p>
          </div>
        </div>
        <button className="text-gray-500 hover:text-gray-700">✖</button>
      </div>

      <div className="mb-4">
        <h3 className="text-sm font-bold text-gray-700">Union</h3>
        <p className="text-sm text-gray-500">Not in a Union</p>
      </div>

      <div className="mb-4">
        <h3 className="text-sm font-bold text-gray-700">Representative Squad</h3>
        <div className="flex space-x-2 mt-2">
          {nikkeDistribution.map((nikke, index) => (
            <div key={index} className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
              <Image src={nikke} alt={`Nikke ${index}`} width={48} height={48} />
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-center">
        <div>
          <h4 className="text-sm font-bold text-gray-700">Squad Power</h4>
          <p className="text-lg font-bold text-gray-900">{squadPower.toFixed(3)}</p>
        </div>
        <div>
          <h4 className="text-sm font-bold text-gray-700">Nikkes Obtained</h4>
          <p className="text-lg font-bold text-gray-900">{nikkeObtained.toString().padStart(3, '0')}</p>
        </div>
        <div>
          <h4 className="text-sm font-bold text-gray-700">Costume</h4>
          <p className="text-lg font-bold text-gray-900">{costume.toString().padStart(3, '0')}</p>
        </div>
        <div>
          <h4 className="text-sm font-bold text-gray-700">Nikke Distribution</h4>
          <p className="text-lg font-bold text-gray-900">{nikkeDistribution.length}</p>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;